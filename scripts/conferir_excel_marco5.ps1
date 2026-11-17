param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot), [string]$Manifesto = '')
$ErrorActionPreference = 'Stop'
$delivery = Join-Path $ProjectRoot 'dados/entregas/marco5'
if ($Manifesto) {
    $configPath = if ([System.IO.Path]::IsPathRooted($Manifesto)) { $Manifesto } else { Join-Path $ProjectRoot $Manifesto }
    $config = Get-Content -LiteralPath $configPath -Raw -Encoding utf8 | ConvertFrom-Json
    $delivery = Join-Path $ProjectRoot $config.diretorio_entrega_proposto
    $resolvedDelivery = [System.IO.Path]::GetFullPath($delivery)
    $allowedBase = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot 'dados/entregas')) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $resolvedDelivery.StartsWith($allowedBase,[System.StringComparison]::OrdinalIgnoreCase)) { throw 'Destino fora da pasta de entregas' }
    if ($resolvedDelivery -eq [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot 'dados/entregas/marco5'))) { throw 'Preservar entrega anterior' }
}
$excel = $null
$book = $null
$log = [System.Collections.Generic.List[object]]::new()
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $excel.AskToUpdateLinks = $false
    $excel.AutomationSecurity = 3
    foreach ($filename in @('Planilha final PIBID.xlsx','Matriz de cobertura e sobreposicao.xlsx')) {
        $book = $excel.Workbooks.Open((Join-Path $delivery $filename), 0, $false)
        $excel.CalculateFullRebuild()
        if ($filename -eq 'Planilha final PIBID.xlsx') {
            foreach ($sheet in $book.Worksheets) {
                if ($sheet.Name -notmatch '^G([1-6]) ') { continue }
                $number = $Matches[1]
                $chart = $sheet.ChartObjects().Item(1).Chart
                if ($number -eq '2' -and $chart.ChartTitle.Text -notmatch '2026: corte 08/11') {
                    $chart.ChartTitle.Text = $chart.ChartTitle.Text + '; 2026: corte 08/11'
                }
                $chart.ChartStyle = 2
                $chart.ChartTitle.Font.Size = 12
                $chart.ChartTitle.IncludeInLayout = $true
                $chart.ChartTitle.Top = 8
                foreach ($axisType in @(1,2)) {
                    [void]$chart.GetType().InvokeMember('HasAxis',[System.Reflection.BindingFlags]::SetProperty,$null,$chart,@($axisType,1,$true))
                    $axis = $chart.Axes($axisType,1)
                    $axis.TickLabelPosition = -4134
                    $axis.TickLabels.Font.Size = 10
                    $axis.TickLabels.Font.Color = 0
                    $axis.TickLabels.Orientation = 0
                }
                $chart.Axes(1,1).TickLabelSpacing = 1
                $chart.Axes(1,1).HasTitle = $false
                $chart.Axes(2,1).HasTitle = $true
                $chart.Axes(2,1).AxisTitle.Text = 'Obras'
                $chart.Axes(2,1).TickLabels.NumberFormat = '0'
                $chart.Axes(2,1).MinimumScale = 0
                $chart.Axes(2,1).MajorGridlines.Format.Line.ForeColor.RGB = 15132390
                $colors = @(6108695,8421376,40934)
                for ($j=1; $j -le $chart.SeriesCollection().Count; $j++) {
                    $series = $chart.SeriesCollection().Item($j)
                    $series.Format.Line.ForeColor.RGB = $colors[$j-1]
                    $series.Format.Fill.ForeColor.RGB = $colors[$j-1]
                    if ($number -eq '1') { $series.Smooth = $false }
                    else {
                        $series.ApplyDataLabels()
                        $series.DataLabels().ShowValue = $true
                        $series.DataLabels().Font.Size = 10
                        $series.DataLabels().Position = 2
                        for ($point=1; $point -le $series.Points().Count; $point++) {
                            $series.Points().Item($point).Format.Fill.ForeColor.RGB = $colors[$j-1]
                        }
                    }
                }
                if ($chart.HasLegend) {
                    $chart.Legend.Position = -4107
                    $chart.Legend.Font.Size = 10
                    $chart.Legend.IncludeInLayout = $true
                }
                $left = 60
                if ($number -in @('3','6')) { $left = 220 }
                $chart.PlotArea.Left = $left
                $chart.PlotArea.Top = 85
                $chart.PlotArea.Width = $chart.ChartArea.Width - $left - 35
                $chart.PlotArea.Height = $chart.ChartArea.Height - 85 - 65
                $sheet.Activate()
                $png = Join-Path $delivery ('previews/G' + $number + '.png')
                $ok = $chart.Export($png, 'PNG')
                if (-not $ok) { throw ('Exportação falhou: ' + $sheet.Name) }
                $sheet.ExportAsFixedFormat(0, (Join-Path $delivery ('previews/G' + $number + '.pdf')))
                $log.Add([pscustomobject]@{aba=$sheet.Name;grafico_nativo=$sheet.ChartObjects().Count;series=$chart.SeriesCollection().Count;primeira_serie=$chart.SeriesCollection().Item(1).Formula;titulo_e_nota=$chart.ChartTitle.Text;png=$png;resultado='OK'})
            }
            $book.Worksheets.Item('Leia-me').Activate()
        }
        $book.Save()
        $log.Add([pscustomobject]@{arquivo=$filename;excel=$excel.Version;abas=$book.Worksheets.Count;recalculo='CalculateFullRebuild';resultado='OK'})
        $book.Close($false)
        $book = $null
    }
} finally {
    if ($null -ne $book) { $book.Close($false) }
    if ($null -ne $excel) { $excel.Quit(); [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($excel) }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
$log | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $delivery 'Conferencia Excel.json') -Encoding utf8
