"""Edge node yönetimi (komut satırı).

Panel API'sinde kullanıcı kimlik doğrulaması olmadığı için edge node oluşturma ve
API anahtarı üretme bilinçli olarak yalnızca bu yerel komutla yapılır.

Kullanım (backend klasöründe):
    python -m app.cli.edge_nodes list
    python -m app.cli.edge_nodes create --factory fac-default --name "Merkez Simülatör" --cameras cam-01,cam-02
    python -m app.cli.edge_nodes assign --node <id> --cameras cam-03,cam-04
    python -m app.cli.edge_nodes unassign --cameras cam-03
    python -m app.cli.edge_nodes rotate-key --node <id>
    python -m app.cli.edge_nodes deactivate --node <id>
"""

import argparse
import sys
from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.core.security import generate_api_key
from app.db.session import get_session_factory
from app.models import Camera, EdgeNode
from app.models.enums import CameraStatus
from app.repositories.edge import EdgeNodeRepository, FactoryRepository


class CliError(Exception):
    pass


def _split(value: str | None) -> list[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def _get_node(session: Session, node_id: str) -> EdgeNode:
    node = EdgeNodeRepository(session).get(node_id)
    if node is None:
        raise CliError(f"Edge node bulunamadı: {node_id}")
    return node


def assign_cameras(session: Session, node: EdgeNode, camera_ids: Sequence[str]) -> list[Camera]:
    """Kameraları edge node'a atar. Kamera, node ile aynı fabrikada olmalıdır."""
    cameras = []
    for camera_id in camera_ids:
        camera = session.get(Camera, camera_id)
        if camera is None:
            raise CliError(f"Kamera bulunamadı: {camera_id}")
        if camera.zone.factory_id != node.factory_id:
            raise CliError(
                f"{camera.code} kamerası {camera.zone.factory_id} fabrikasında; "
                f"node ise {node.factory_id} fabrikasında."
            )
        camera.edge_node_id = node.id
        # Gerçek telemetri gelene kadar durum bilinmez
        camera.status = CameraStatus.UNKNOWN
        cameras.append(camera)
    return cameras


def create_node(
    session: Session, *, factory_id: str, name: str, camera_ids: Sequence[str] = ()
) -> tuple[EdgeNode, str]:
    if FactoryRepository(session).get(factory_id) is None:
        raise CliError(f"Fabrika bulunamadı: {factory_id}")
    key = generate_api_key()
    node = EdgeNode(
        factory_id=factory_id, name=name, api_key_hash=key.hash, api_key_prefix=key.prefix
    )
    EdgeNodeRepository(session).add(node)
    session.flush()
    assign_cameras(session, node, camera_ids)
    session.commit()
    return node, key.key


def rotate_key(session: Session, node: EdgeNode) -> str:
    key = generate_api_key()
    node.api_key_hash = key.hash
    node.api_key_prefix = key.prefix
    session.commit()
    return key.key


def _print_key(node: EdgeNode, key: str) -> None:
    print(f"\nEdge node: {node.id} ({node.name}) · fabrika: {node.factory_id}")
    print("API anahtarı (yalnızca şimdi gösterilir, güvenli bir yerde saklayın):\n")
    print(f"    {key}\n")
    print("vision/.env dosyasına ekleyin:  EDGE_API_KEY=<yukarıdaki anahtar>")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.cli.edge_nodes")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="Edge node'ları ve atanmış kameraları listele")

    p = sub.add_parser("create", help="Yeni edge node ve API anahtarı oluştur")
    p.add_argument("--factory", required=True, help="Fabrika kimliği, ör. fac-default")
    p.add_argument("--name", required=True)
    p.add_argument("--cameras", help="Virgülle ayrılmış kamera kimlikleri")

    p = sub.add_parser("assign", help="Kameraları bir edge node'a ata")
    p.add_argument("--node", required=True)
    p.add_argument("--cameras", required=True)

    p = sub.add_parser("unassign", help="Kameraların edge atamasını kaldır")
    p.add_argument("--cameras", required=True)

    p = sub.add_parser("rotate-key", help="API anahtarını yenile (eski anahtar geçersiz olur)")
    p.add_argument("--node", required=True)

    p = sub.add_parser("deactivate", help="Edge node'u devre dışı bırak")
    p.add_argument("--node", required=True)

    args = parser.parse_args(argv)

    with get_session_factory()() as session:
        try:
            if args.command == "list":
                nodes = EdgeNodeRepository(session).list()
                if not nodes:
                    print("Kayıtlı edge node yok.")
                for n in nodes:
                    cams = ", ".join(c.id for c in n.cameras) or "-"
                    state = "etkin" if n.is_active else "devre dışı"
                    seen = n.last_seen_at.isoformat() if n.last_seen_at else "hiç"
                    print(
                        f"{n.id}  {n.name}  [{state}]  fabrika={n.factory_id}  "
                        f"anahtar={n.api_key_prefix}…  son görülme={seen}  kameralar={cams}"
                    )
            elif args.command == "create":
                node, key = create_node(
                    session,
                    factory_id=args.factory,
                    name=args.name,
                    camera_ids=_split(args.cameras),
                )
                _print_key(node, key)
            elif args.command == "assign":
                node = _get_node(session, args.node)
                cams = assign_cameras(session, node, _split(args.cameras))
                session.commit()
                print(f"{len(cams)} kamera {node.id} node'una atandı.")
            elif args.command == "unassign":
                for camera_id in _split(args.cameras):
                    camera = session.get(Camera, camera_id)
                    if camera is None:
                        raise CliError(f"Kamera bulunamadı: {camera_id}")
                    camera.edge_node_id = None
                    camera.status = CameraStatus.UNKNOWN
                session.commit()
                print("Atama kaldırıldı.")
            elif args.command == "rotate-key":
                node = _get_node(session, args.node)
                _print_key(node, rotate_key(session, node))
            elif args.command == "deactivate":
                node = _get_node(session, args.node)
                node.is_active = False
                session.commit()
                print(f"{node.id} devre dışı bırakıldı; anahtarı artık kabul edilmez.")
        except CliError as exc:
            session.rollback()
            print(f"Hata: {exc}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
