import os
import sys
import subprocess

def export_pptx_slides(pptx_path, out_dir=None):
    abs_pptx = os.path.abspath(pptx_path)
    if not os.path.exists(abs_pptx):
        print(f"Error: {abs_pptx} not found")
        return []
    
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(abs_pptx), "slides_preview")
    abs_out = os.path.abspath(out_dir)
    os.makedirs(abs_out, exist_ok=True)
    
    # PowerShell script to export slides via native PowerPoint COM
    ps_script = f'''
$pptxPath = (Resolve-Path '{abs_pptx}').Path
$outDir = '{abs_out}'
$ppt = New-Object -ComObject PowerPoint.Application
try {{
    $pres = $ppt.Presentations.Open($pptxPath, 1, 0, 0)
    $i = 1
    foreach ($slide in $pres.Slides) {{
        $outImg = Join-Path $outDir ("slide_" + $i.ToString("D2") + ".png")
        $slide.Export($outImg, "PNG", 1920, 1080)
        $i++
    }}
    $pres.Close()
}} finally {{
    $ppt.Quit()
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}}
Write-Host "Export completed to $outDir"
'''
    ps_file = os.path.join(abs_out, "export.ps1")
    with open(ps_file, "w", encoding="utf-8-sig") as f:
        f.write(ps_script)
        
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(ps_file):
        os.remove(ps_file)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)
        
    imgs = [os.path.join(abs_out, f) for f in sorted(os.listdir(abs_out)) if f.endswith(".png")]
    return imgs

if __name__ == '__main__':
    pptx = sys.argv[1] if len(sys.argv) > 1 else "合思敏捷业财解决方案演示.pptx"
    export_pptx_slides(pptx)
