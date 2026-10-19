import { useMemo, useState } from 'react'
import { getRouteApi } from '@tanstack/react-router'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { DemoNotice } from '@/components/demo-notice'
import { AppHeader } from '@/components/layout/app-header'
import { Main } from '@/components/layout/main'
import { PageHeading } from '@/components/page-heading'
import { CameraDetailPanel } from './components/camera-detail-panel'
import { CameraFilters } from './components/camera-filters'
import { CameraGrid } from './components/camera-grid'
import { CameraSummaryCards } from './components/camera-summary-cards'
import { ViolationFeed } from './components/violation-feed'
import { ViolationHistoryTable } from './components/violation-history-table'
import { useCameras, useViolations } from './hooks/use-camera-queries'
import {
  DEFAULT_CAMERA_FILTERS,
  filterCameras,
  type CameraFilterState,
} from './lib/filters'

const route = getRouteApi('/_authenticated/cameras/')

export function Cameras() {
  // Seçili kamera ve sekme URL'de tutulur; bağlantı paylaşılabilir.
  const { camera: selectedId, tab = 'cameras' } = route.useSearch()
  const navigate = route.useNavigate()
  const [filters, setFilters] = useState<CameraFilterState>(
    DEFAULT_CAMERA_FILTERS
  )

  const { data: cameras = [], isLoading } = useCameras()
  const { data: openViolations = [] } = useViolations({ status: ['open'] })

  const camerasById = useMemo(
    () => new Map(cameras.map((c) => [c.id, c])),
    [cameras]
  )
  const zones = useMemo(
    () => [...new Map(cameras.map((c) => [c.zone.id, c.zone])).values()],
    [cameras]
  )
  const openViolationsByCamera = useMemo(() => {
    const counts: Record<string, number> = {}
    for (const v of openViolations)
      counts[v.cameraId] = (counts[v.cameraId] ?? 0) + 1
    return counts
  }, [openViolations])

  const visibleCameras = filterCameras(cameras, filters)
  const selectedCamera = selectedId ? camerasById.get(selectedId) : undefined

  const selectCamera = (cameraId: string | undefined) =>
    navigate({ search: (prev) => ({ ...prev, camera: cameraId }) })

  return (
    <>
      <AppHeader />

      <Main fluid className='space-y-6'>
        <PageHeading
          title='Kamera Yönetimi'
          description='Kamera görüntüleri ve KKD (baret, reflektörlü yelek) denetimi'
          actions={
            <Badge variant='outline' className='border-warning/40 text-warning'>
              Örnek veri · Simülasyon
            </Badge>
          }
        />

        <DemoNotice />

        <CameraSummaryCards />

        <Tabs
          value={tab}
          onValueChange={(value) =>
            navigate({
              search: (prev) => ({
                ...prev,
                tab: value === 'cameras' ? undefined : (value as 'history'),
              }),
            })
          }
          className='gap-4'
        >
          <TabsList>
            <TabsTrigger value='cameras'>Kameralar</TabsTrigger>
            <TabsTrigger value='history'>İhlal Geçmişi</TabsTrigger>
          </TabsList>

          <TabsContent value='cameras'>
            <div className='grid gap-6 xl:grid-cols-[minmax(0,1fr)_22rem]'>
              <div className='space-y-4'>
                <CameraFilters
                  value={filters}
                  onChange={setFilters}
                  zones={zones}
                  resultCount={visibleCameras.length}
                />
                <CameraGrid
                  cameras={visibleCameras}
                  isLoading={isLoading}
                  selectedId={selectedId}
                  openViolationsByCamera={openViolationsByCamera}
                  onSelect={(camera) => selectCamera(camera.id)}
                />
              </div>
              <aside>
                <ViolationFeed
                  camerasById={camerasById}
                  onSelectCamera={selectCamera}
                />
              </aside>
            </div>
          </TabsContent>

          <TabsContent value='history'>
            <ViolationHistoryTable cameras={cameras} />
          </TabsContent>
        </Tabs>
      </Main>

      <CameraDetailPanel
        camera={selectedCamera}
        onClose={() => selectCamera(undefined)}
      />
    </>
  )
}
