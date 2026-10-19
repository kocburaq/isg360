import { type FactoryZone } from '@/types/factory'
import { Search, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { CAMERA_STATUS } from '../config/status'
import { DEFAULT_CAMERA_FILTERS, type CameraFilterState } from '../lib/filters'

type CameraFiltersProps = {
  value: CameraFilterState
  onChange: (value: CameraFilterState) => void
  zones: FactoryZone[]
  resultCount: number
}

export function CameraFilters({
  value,
  onChange,
  zones,
  resultCount,
}: CameraFiltersProps) {
  const isFiltered =
    value.search !== '' || value.status !== 'all' || value.zoneId !== 'all'

  return (
    <div className='flex flex-wrap items-center gap-2'>
      <div className='relative w-full sm:w-64'>
        <Search className='pointer-events-none absolute start-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground' />
        <Input
          value={value.search}
          onChange={(e) => onChange({ ...value, search: e.target.value })}
          placeholder='Ad, kod veya konum ara'
          aria-label='Kamera ara'
          className='h-9 ps-8'
        />
      </div>

      <Select
        value={value.status}
        onValueChange={(status) =>
          onChange({ ...value, status: status as CameraFilterState['status'] })
        }
      >
        <SelectTrigger className='h-9 w-40' aria-label='Duruma göre filtrele'>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='all'>Tüm durumlar</SelectItem>
          {Object.entries(CAMERA_STATUS).map(([status, meta]) => (
            <SelectItem key={status} value={status}>
              {meta.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select
        value={value.zoneId}
        onValueChange={(zoneId) => onChange({ ...value, zoneId })}
      >
        <SelectTrigger className='h-9 w-52' aria-label='Bölgeye göre filtrele'>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='all'>Tüm bölgeler</SelectItem>
          {zones.map((zone) => (
            <SelectItem key={zone.id} value={zone.id}>
              {zone.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {isFiltered && (
        <Button
          variant='ghost'
          size='sm'
          onClick={() => onChange(DEFAULT_CAMERA_FILTERS)}
        >
          Temizle
          <X />
        </Button>
      )}

      <span
        className='ms-auto text-sm text-muted-foreground'
        aria-live='polite'
      >
        {resultCount} kamera
      </span>
    </div>
  )
}
