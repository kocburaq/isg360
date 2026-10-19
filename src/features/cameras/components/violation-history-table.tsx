import { useMemo, useState } from 'react'
import {
  type ColumnDef,
  type ColumnFiltersState,
  type FilterFn,
  type SortingState,
  flexRender,
  getCoreRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table'
import { formatDateTime, formatPercent } from '@/lib/format'
import { cn } from '@/lib/utils'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DataTableColumnHeader,
  DataTablePagination,
  DataTableToolbar,
} from '@/components/data-table'
import { getPpeClass, PPE_CLASSES } from '../config/ppe-classes'
import { VIOLATION_SEVERITY, VIOLATION_STATUS } from '../config/status'
import { useViolations } from '../hooks/use-camera-queries'
import { type Camera, type PpeViolation } from '../types'
import { ViolationStatusBadge } from './violation-status-badge'

type ViolationHistoryTableProps = {
  cameras: Camera[]
}

const includesValue: FilterFn<PpeViolation> = (row, id, value: string[]) =>
  value.includes(row.getValue(id))

const includesAny: FilterFn<PpeViolation> = (row, id, value: string[]) =>
  value.some((v) => row.getValue<string[]>(id).includes(v))

export function ViolationHistoryTable({ cameras }: ViolationHistoryTableProps) {
  const { data = [], isLoading } = useViolations()
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'detectedAt', desc: true },
  ])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = useState('')

  const camerasById = useMemo(
    () => new Map(cameras.map((c) => [c.id, c])),
    [cameras]
  )

  const columns = useMemo<ColumnDef<PpeViolation>[]>(
    () => [
      {
        accessorKey: 'detectedAt',
        meta: { label: 'Zaman' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Zaman' />
        ),
        cell: ({ row }) => (
          <span className='whitespace-nowrap tabular-nums'>
            {formatDateTime(row.original.detectedAt)}
          </span>
        ),
      },
      {
        accessorKey: 'cameraId',
        meta: { label: 'Kamera' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Kamera' />
        ),
        cell: ({ row }) => {
          const camera = camerasById.get(row.original.cameraId)
          return (
            <div className='min-w-40'>
              <p className='font-medium'>{camera?.name ?? '—'}</p>
              <p className='text-xs text-muted-foreground'>
                {camera?.code} · {camera?.zone.name}
              </p>
            </div>
          )
        },
        filterFn: includesValue,
      },
      {
        accessorKey: 'missing',
        meta: { label: 'Eksik KKD' },
        header: 'Eksik KKD',
        enableSorting: false,
        cell: ({ row }) => (
          <div className='flex flex-wrap gap-x-3 gap-y-1'>
            {row.original.missing.map((id) => {
              const ppe = getPpeClass(id)
              return (
                <span
                  key={id}
                  className='inline-flex items-center gap-1 whitespace-nowrap'
                >
                  <ppe.icon className='size-3.5 text-destructive' />
                  {ppe.label}
                </span>
              )
            })}
          </div>
        ),
        filterFn: includesAny,
      },
      {
        accessorKey: 'severity',
        meta: { label: 'Önem' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Önem' />
        ),
        cell: ({ row }) => {
          const meta = VIOLATION_SEVERITY[row.original.severity]
          return <span className={cn(meta.className)}>{meta.label}</span>
        },
        filterFn: includesValue,
      },
      {
        accessorKey: 'confidence',
        meta: { label: 'Güven' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Güven' />
        ),
        cell: ({ row }) => (
          <span className='tabular-nums'>
            {formatPercent(row.original.confidence)}
          </span>
        ),
      },
      {
        accessorKey: 'status',
        meta: { label: 'Durum' },
        header: ({ column }) => (
          <DataTableColumnHeader column={column} title='Durum' />
        ),
        cell: ({ row }) => (
          <ViolationStatusBadge status={row.original.status} />
        ),
        filterFn: includesValue,
      },
    ],
    [camerasById]
  )

  // eslint-disable-next-line react-hooks/incompatible-library
  const table = useReactTable({
    data,
    columns,
    state: { sorting, columnFilters, globalFilter },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: (row, _id, value: string) => {
      const camera = camerasById.get(row.original.cameraId)
      const haystack = [
        camera?.code,
        camera?.name,
        camera?.zone.name,
        row.original.id,
      ]
        .join(' ')
        .toLocaleLowerCase('tr-TR')
      return haystack.includes(value.trim().toLocaleLowerCase('tr-TR'))
    },
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    initialState: { pagination: { pageSize: 10 } },
  })

  return (
    <div className='space-y-4'>
      <DataTableToolbar
        table={table}
        searchPlaceholder='Kamera veya bölge ara...'
        filters={[
          {
            columnId: 'status',
            title: 'Durum',
            options: Object.entries(VIOLATION_STATUS).map(([value, m]) => ({
              value,
              label: m.label,
            })),
          },
          {
            columnId: 'missing',
            title: 'KKD',
            options: PPE_CLASSES.filter((c) => c.enabled).map((c) => ({
              value: c.id,
              label: c.label,
              icon: c.icon,
            })),
          },
          {
            columnId: 'severity',
            title: 'Önem',
            options: Object.entries(VIOLATION_SEVERITY).map(([value, m]) => ({
              value,
              label: m.label,
            })),
          },
          {
            columnId: 'cameraId',
            title: 'Kamera',
            options: cameras.map((c) => ({ value: c.id, label: c.code })),
          },
        ]}
      />

      <div className='overflow-hidden rounded-md border'>
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((group) => (
              <TableRow key={group.id}>
                {group.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell colSpan={columns.length}>
                    <Skeleton className='h-6 w-full' />
                  </TableCell>
                </TableRow>
              ))
            ) : table.getRowModel().rows.length > 0 ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className='h-24 text-center text-muted-foreground'
                >
                  Kayıt bulunamadı.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <DataTablePagination table={table} />
    </div>
  )
}
