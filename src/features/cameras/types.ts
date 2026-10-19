import { type EntityId, type ISODateString } from '@/types/common'
import { type EntityRef, type FactoryZone } from '@/types/factory'

/* ------------------------------------------------------------------ */
/* Kamera                                                              */
/* ------------------------------------------------------------------ */

/** "unknown": gerçek telemetri yok (ör. API ile yeni eklenen kamera). */
export type CameraStatus = 'online' | 'offline' | 'unknown'

export type Camera = {
  id: EntityId
  /** Saha etiketi, ör. "CAM-01". */
  code: string
  name: string
  zone: FactoryZone
  /** Kameranın fiziksel konumu (serbest metin). */
  location: string
  status: CameraStatus
  /** Son sinyal alınan zaman; hiç sinyal alınmadıysa null. */
  lastSeenAt: ISODateString | null
  stream: {
    protocol: 'rtsp'
    /** Gerçek RTSP adresi backend'de tutulur; arayüze gönderilmez. */
    configured: boolean
    resolution: string
    fps: number
  }
  /** Bu kamerada denetlenen KKD sınıfları. */
  ppeClasses: PpeClassId[]
  /** true: durum ve kayıtlar simülasyon/örnek veridir, gerçek telemetri değildir. */
  isSimulated: boolean
  createdAt?: ISODateString
  updatedAt?: ISODateString
}

/* ------------------------------------------------------------------ */
/* KKD (Kişisel Koruyucu Donanım)                                      */
/* ------------------------------------------------------------------ */

/**
 * Desteklenen ve planlanan KKD sınıfları.
 * Yeni sınıf eklemek için buraya kimlik, `config/ppe-classes.ts` içine tanım eklenir.
 */
export type PpeClassId =
  'helmet' | 'vest' | 'gloves' | 'goggles' | 'safety-boots'

/** Bir kişi için tek bir KKD sınıfının tespit sonucu. */
export type PpeCheckState = 'compliant' | 'violation' | 'unknown'

export type PpeCheck = {
  classId: PpeClassId
  state: PpeCheckState
  /** Model güven skoru (0–1). */
  confidence: number
}

/** Görüntüde 0–1 aralığında normalize edilmiş sınırlayıcı kutu. */
export type BoundingBox = {
  x: number
  y: number
  width: number
  height: number
}

export type PersonDetection = {
  id: EntityId
  box: BoundingBox
  checks: PpeCheck[]
}

/**
 * Bir kameradan alınan son tespit sonucu.
 * `source: 'simulation'` olan kayıtlar gerçek model çıktısı DEĞİLDİR.
 */
export type DetectionSnapshot = {
  cameraId: EntityId
  capturedAt: ISODateString
  source: 'simulation' | 'model'
  /** Gerçek entegrasyonda model adı/sürümü (ör. "yolov8n-ppe@1.2"). */
  model: string | null
  persons: PersonDetection[]
}

/* ------------------------------------------------------------------ */
/* İhlaller                                                            */
/* ------------------------------------------------------------------ */

export type ViolationStatus = 'open' | 'acknowledged' | 'resolved'
export type ViolationSeverity = 'low' | 'medium' | 'high'

export type PpeViolation = {
  id: EntityId
  cameraId: EntityId
  zoneId: EntityId
  /** Eksik tespit edilen KKD sınıfları. */
  missing: PpeClassId[]
  detectedAt: ISODateString
  confidence: number
  severity: ViolationSeverity
  status: ViolationStatus
  source: DetectionSnapshot['source']
  /** İnceleme notu / açıklama. */
  description: string | null
  /** Açık durumdan çıkıldığı (incelendiği) zaman. */
  reviewedAt: ISODateString | null
  /** İleride bağlanacak kayıtlar (ör. düzeltici faaliyet iş kartı). */
  links: EntityRef[]
}

export type ViolationQuery = {
  cameraId?: EntityId
  status?: ViolationStatus[]
}

/* ------------------------------------------------------------------ */
/* Sistem durumu                                                       */
/* ------------------------------------------------------------------ */

export type ServiceState = 'operational' | 'degraded' | 'down' | 'simulated'

export type ServiceHealth = {
  id: string
  label: string
  state: ServiceState
  detail: string
}

/** Panel özet kartları (backend: GET /dashboard/summary). */
export type CameraSummary = {
  cameras: { total: number; online: number; offline: number; unknown: number }
  violations: {
    total: number
    today: number
    open: number
    acknowledged: number
    resolved: number
  }
  containsSimulatedData: boolean
  generatedAt: ISODateString
}

export type SystemStatus = {
  state: ServiceState
  checkedAt: ISODateString
  services: ServiceHealth[]
}
