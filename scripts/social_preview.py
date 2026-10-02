from pathlib import Path
import re, base64, io
from PIL import Image, ImageDraw, ImageFont

page = Path('index.html')
text = page.read_text(encoding='utf-8')

# Extract the original ARDAS header logo already embedded in the production HTML.
key_match = re.search(r'<img class="brand-logo"[^>]*data-ardas-img="([^"]+)"', text)
if not key_match:
    raise SystemExit('ARDAS logo key not found')
key = key_match.group(1)
uri_match = re.search(r'"' + re.escape(key) + r'":"(data:image/[^;]+;base64,[A-Za-z0-9+/=]+)"', text)
if not uri_match:
    raise SystemExit('Embedded ARDAS logo data not found')
raw = base64.b64decode(uri_match.group(1).split(',', 1)[1])
logo = Image.open(io.BytesIO(raw)).convert('RGBA')

# Create a 1200x630 share card using the original logo.
W, H = 1200, 630
canvas = Image.new('RGB', (W, H), '#f7fbff')
draw = ImageDraw.Draw(canvas)
draw.ellipse((850, -220, 1350, 280), fill='#e8f5fd')
draw.ellipse((-260, 390, 260, 910), fill='#edf6ff')
draw.rounded_rectangle((65, 65, W-65, H-65), radius=42, fill='white', outline='#dbe8f4', width=2)

scale = min(820 / logo.width, 350 / logo.height)
logo = logo.resize((max(1, int(logo.width * scale)), max(1, int(logo.height * scale))), Image.Resampling.LANCZOS)
canvas.paste(logo, ((W-logo.width)//2, 100), logo)

try:
    font_bold = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
    font_reg = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 23)
except Exception:
    font_bold = ImageFont.load_default()
    font_reg = ImageFont.load_default()

tagline = 'Kurumsal Gelişim • Eğitim • Bilim • Teknoloji'
domain = 'www.ardas.com.tr'
tb = draw.textbbox((0,0), tagline, font=font_bold)
draw.text(((W-(tb[2]-tb[0]))/2, 455), tagline, font=font_bold, fill='#082f5a')
db = draw.textbbox((0,0), domain, font=font_reg)
draw.text(((W-(db[2]-db[0]))/2, 510), domain, font=font_reg, fill='#62778e')
canvas.save('og-image.png', 'PNG', optimize=True)

# Replace only metadata; visible site layout/content is untouched.
text = re.sub(r'\s*<link rel="canonical"[^>]*>', '', text)
text = re.sub(r'\s*<meta property="og:[^"]+"[^>]*>', '', text)
text = re.sub(r'\s*<meta name="twitter:[^"]+"[^>]*>', '', text)

description_match = re.search(r'<meta name="description"[^>]*>', text)
if not description_match:
    raise SystemExit('Description meta not found')

social = '''
<link rel="canonical" href="https://www.ardas.com.tr/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ARDAS">
<meta property="og:title" content="ARDAS | Kurumsal Gelişim, Eğitim, Bilim ve Teknoloji">
<meta property="og:description" content="ARDAS eğitim kurumları için kurumsal gelişim, danışmanlık, bilim, eğitim ve teknoloji çözümleri sunar.">
<meta property="og:url" content="https://www.ardas.com.tr/">
<meta property="og:image" content="https://www.ardas.com.tr/og-image.png">
<meta property="og:image:secure_url" content="https://www.ardas.com.tr/og-image.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="ARDAS">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="ARDAS | Kurumsal Gelişim, Eğitim, Bilim ve Teknoloji">
<meta name="twitter:description" content="ARDAS eğitim kurumları için kurumsal gelişim, danışmanlık, bilim, eğitim ve teknoloji çözümleri sunar.">
<meta name="twitter:image" content="https://www.ardas.com.tr/og-image.png">
'''
pos = description_match.end()
text = text[:pos] + social + text[pos:]
page.write_text(text, encoding='utf-8')
