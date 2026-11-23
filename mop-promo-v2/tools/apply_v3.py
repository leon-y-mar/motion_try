"""v3: personajes construidos desde las referencias + retiro de la tarjeta no mapeada en Figma."""
import pathlib
p = pathlib.Path(__file__).parent.parent / "src.html"
s = p.read_text()


def cut(s, start, end_marker):
    a = s.index(start)
    b = s.index(end_marker, a)
    return s[:a], s[b:]


# 1) quitar los generadores SVG anteriores
a = s.index('/* ═════════════ characters ═════════════ */')
b = s.index('/* ═════════════ quote text ═════════════ */')
s = s[:a] + '''/* ═════════════ characters ═════════════
   Construidos desde las referencias del usuario (tools/make_characters.py):
   barista.png y ale_happy.png son las referencias sin fondo; ale_pensive.png es la
   referencia recortada (sin café) y sin rasgos; la expresión pensativa se dibuja en
   vector encima (#aleFace), en coordenadas del original (viewBox 104 0 280 482). */
''' + s[b:]

# 2) Alejandra pensativa + rasgos vectoriales
s = s.replace('<div id="aleWrap"></div>', '''<div id="aleWrap">
    <img src="assets/ale_pensive.png" style="position:absolute;left:0;top:0;width:540px;height:930px">
    <svg id="aleFace" viewBox="104 0 280 482" style="position:absolute;left:0;top:0;width:540px;height:930px;overflow:visible">
      <g id="aBrows" stroke="#271A0A" stroke-width="3.2" fill="none" stroke-linecap="round">
        <path d="M137.5,111.5 Q145,107 154,105.5"/><path d="M174,104.5 Q187,102.5 201.5,108.5"/></g>
      <g id="aEyeL"><ellipse cx="145" cy="127.5" rx="4.6" ry="5.8" fill="#212620"/><circle cx="146.8" cy="125.2" r="1.4" fill="#fff"/></g>
      <g id="aEyeR"><ellipse cx="186.5" cy="126" rx="4.6" ry="5.8" fill="#212620"/><circle cx="188.3" cy="123.7" r="1.4" fill="#fff"/></g>
      <path id="aMouth" d="M158.5,181.5 Q167,178.6 177.5,180.6" stroke="#B23610" stroke-width="2.8" fill="none" stroke-linecap="round"/>
      <g id="aThink">
        <circle cx="300" cy="88" r="4" fill="#fff"/><circle cx="314" cy="70" r="6.5" fill="#fff"/>
        <rect x="312" y="24" width="64" height="34" rx="17" fill="#fff"/>
        <circle class="dot" cx="331" cy="41" r="3.6" fill="#1E3932"/><circle class="dot" cx="344" cy="41" r="3.6" fill="#1E3932"/><circle class="dot" cx="357" cy="41" r="3.6" fill="#1E3932"/></g>
    </svg></div>''')
s = s.replace('#aleWrap{position:absolute;left:1180px;top:150px;width:620px;height:930px}',
              '#aleWrap{position:absolute;left:1220px;top:150px;width:540px;height:930px}')

# 3) barista y Alejandra feliz como imágenes de referencia
s = s.replace('<div id="barWrap"></div>',
              '<div id="barWrap"><img src="assets/barista.png" style="width:576px;height:640px;display:block"></div>')
s = s.replace('#barWrap{position:absolute;left:1262px;top:300px;width:620px;height:780px;transform-origin:50% 100%}',
              '#barWrap{position:absolute;left:150px;top:440px;width:576px;height:640px;transform-origin:50% 100%}')
s = s.replace('<div id="aleHappyWrap"></div>',
              '<div id="aleHappyWrap"><img src="assets/ale_happy.png" style="width:717px;height:900px;display:block"></div>')
s = s.replace('#aleHappyWrap{position:absolute;left:1180px;top:160px;width:620px;height:930px}',
              '#aleHappyWrap{position:absolute;left:1120px;top:180px;width:717px;height:900px}')

# 4) textos a la derecha del teléfono (el barista ocupa la izquierda)
s = s.replace('#cap{position:absolute;left:140px;top:380px;width:560px}',
              '#cap{position:absolute;left:1262px;top:380px;width:560px}')

# 5) retirar la tarjeta "Tu pedido te espera" (no está mapeada en Figma)
a = s.index('<div id="trReady"')
b = s.index('Sin hacer cola', a)
b = s.index('</div></div>', b) + len('</div></div>')
s = s[:a] + s[b:]
s = s.replace(" const rd=st===3?E.back(seg(t,s.stepAt+.3,s.stepAt+.8)):0;css('trReady',{opacity:clamp(rd),transform:`translateY(${(1-rd)*30}px)`});\n", "")

# 6) animación: parpadeo/mirada de Alejandra, empuje del barista
s = s.replace("""  const blink=(t%3.2)>3.05?.15:1;const eyes=document.querySelector('#aleWrap #aEyes');if(eyes){eyes.style.transformOrigin='317px 300px';eyes.style.transform=`scaleY(${blink}) translate(${Math.sin(t*.6)*3}px,${-3+Math.cos(t*.5)*2}px)`}""",
"""  const blink=(t%3.2)>3.06?.12:1;
  [['aEyeL','145px 127.5px'],['aEyeR','186.5px 126px']].forEach(([id,o])=>css(id,{transformOrigin:o,transform:`translate(${1.2+Math.sin(t*.6)*.8}px,${-1+Math.cos(t*.5)*.6}px) scaleY(${blink})`}));
  css('aBrows',{transform:`translateY(${-Math.max(0,Math.sin(t*.9))*1.2}px)`});
  css('aThink',{transformOrigin:'300px 88px',transform:`scale(${E.back(seg(t,1.0,1.5))})`});""")
s = s.replace("""  const arm=document.querySelector('#barWrap #bArm');if(arm){arm.style.transformOrigin='182px 556px';arm.style.transform=`rotate(${Math.sin(vt*2.2)*3}deg)`}
  const bh=document.querySelector('#barWrap #bHead');if(bh){bh.style.transformOrigin='300px 440px';bh.style.transform=`rotate(${Math.sin(vt*1.1)*2-2}deg)`}
  const be=document.querySelector('#barWrap #bEyes');if(be){be.style.transformOrigin='303px 318px';be.style.transform=`scaleY(${(vt%3.7)>3.55?.15:1})`}
""", "")
s = s.replace("css('barWrap',{opacity:clamp(bIn*1.5),transform:`translateY(${(1-bIn)*420}px) rotate(${Math.sin(vt*1.3)*1.2}deg)`});",
              "css('barWrap',{opacity:clamp(bIn*1.5),transform:`translate(${Math.max(0,Math.sin(vt*2.4))*6}px,${(1-bIn)*560+Math.sin(vt*1.3)*3}px) rotate(${Math.sin(vt*1.1)*.8}deg)`});")
p.write_text(s)
for k in ['alejandra(', 'barista()', 'trReady', 'bArm', 'aEyes', 'ale_pensive.png', 'barista.png']:
    print(k, s.count(k))
