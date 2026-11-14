// Deck v3: reveal.js setup and the drill-in sheets (chips in each slide's foot).
// One sheet open at a time; Esc, the scrim or × closes it; changing slide closes it too.
(function () {
  Reveal.initialize({
    hash: true, slideNumber: 'c/t', width: 1280, height: 720, margin: 0.04,
    center: false, transition: 'fade', transitionSpeed: 'fast', plugins: [RevealNotes],
  })

  let open = null
  function close() {
    if (!open) return
    open.sheet.hidden = true
    open.chip.setAttribute('aria-expanded', 'false')
    open.chip.focus({ preventScroll: true })
    open = null
  }
  function show(chip) {
    const sheet = document.getElementById(chip.dataset.drill)
    if (!sheet) return
    close()
    sheet.hidden = false
    chip.setAttribute('aria-expanded', 'true')
    open = { sheet, chip }
    sheet.querySelector('.sheet-close')?.focus({ preventScroll: true })
  }

  document.addEventListener('click', (event) => {
    const chip = event.target.closest('.chip[data-drill]')
    if (chip) { event.preventDefault(); show(chip); return }
    if (open && event.target.closest('[data-close]')) { event.preventDefault(); close() }
  })
  // Capture phase on window runs before reveal's own keyboard handler on document.
  window.addEventListener('keydown', (event) => {
    if (!open) return
    if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); close() }
    else if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' ', 'PageUp', 'PageDown'].includes(event.key)) {
      event.stopPropagation() // keep the slide still while reading a sheet
    }
  }, true)
  Reveal.on('slidechanged', close)

  // "Next" hint: a big arrow that flies into reveal's small chevron, so a first-time viewer
  // sees where "next" lives. Plays on load and again after IDLE_MS while the viewer has not
  // moved yet; stops for good after the first slide change. Not in print or speaker view.
  const IDLE_MS = 9000
  if (/print-pdf|receiver/.test(location.search)) return
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches
  const hint = document.createElement('button')
  hint.type = 'button'
  hint.className = 'next-hint'
  hint.setAttribute('aria-label', 'Next slide')
  hint.hidden = true
  hint.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13 5.5 19.5 12 13 18.5"/></svg><span class="next-hint-label">Next</span>'
  hint.addEventListener('click', () => Reveal.next())
  document.body.appendChild(hint)

  let moved = false
  let idle = null
  let running = []
  const chevron = () => document.querySelector('.reveal .controls .navigate-right.enabled')

  function stop() {
    running.forEach((a) => a.cancel())
    running = []
    hint.hidden = true
  }
  function ring(target) {
    target.classList.remove('nudge')
    void target.offsetWidth // restart the CSS animation
    target.classList.add('nudge')
    setTimeout(() => target.classList.remove('nudge'), 2400)
  }
  async function play() {
    const target = chevron()
    if (moved || running.length || !target || open || document.hidden) return
    if (reduce) { ring(target); return }
    hint.hidden = false
    const from = hint.getBoundingClientRect()
    const to = target.getBoundingClientRect()
    const dx = to.left + to.width / 2 - (from.left + from.width / 2)
    const dy = to.top + to.height / 2 - (from.top + from.height / 2)
    const scale = Math.max(to.width, to.height) / from.width
    const label = hint.querySelector('.next-hint-label')
    const steps = [
      () => hint.animate(
        [{ opacity: 0, transform: 'scale(0.5)' }, { opacity: 1, transform: 'scale(1.08)', offset: 0.7 }, { opacity: 1, transform: 'scale(1)' }],
        { duration: 450, easing: 'ease-out' }),
      () => hint.animate(
        [{ transform: 'translateX(0)' }, { transform: 'translateX(14px)' }, { transform: 'translateX(0)' }, { transform: 'translateX(14px)' }, { transform: 'translateX(0)' }],
        { duration: 1300, easing: 'ease-in-out' }),
      () => {
        label.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 200, fill: 'forwards' })
        return hint.animate(
          [{ transform: 'translate(0, 0) scale(1)', opacity: 1 }, { transform: `translate(${dx}px, ${dy}px) scale(${scale})`, opacity: 0.9, offset: 0.9 }, { transform: `translate(${dx}px, ${dy}px) scale(${scale})`, opacity: 0 }],
          { duration: 750, easing: 'cubic-bezier(0.55, 0, 0.3, 1)', fill: 'forwards' })
      },
    ]
    try {
      for (const step of steps) {
        const anim = step()
        running = [anim]
        await anim.finished
      }
    } catch { return } // cancelled by stop()
    label.getAnimations().forEach((a) => a.cancel())
    stop()
    ring(target)
    schedule()
  }
  function schedule() {
    clearTimeout(idle)
    if (!moved) idle = setTimeout(play, IDLE_MS)
  }

  const start = () => setTimeout(play, 900)
  if (Reveal.isReady()) start(); else Reveal.on('ready', start)
  Reveal.on('slidechanged', () => {
    moved = true
    clearTimeout(idle)
    stop()
  })
  addEventListener('resize', stop)

  // Arrival animations (not in print or speaker view: the early return above covers both).
  //  - .kicker-intro slides: the kicker opens large in the centre, then moves to its place while the
  //    rest of the slide fades in. Only when arriving forward, so stepping back stays calm.
  //  - embedded pages (the pathway diagram) animate in when their slide is shown: the deck sends
  //    {silta: 'play'} to the frame, and {silta: 'prime'} to every other frame so it is ready, hidden,
  //    before its slide fades in. A frame that loads late asks with {silta: 'ready?'}.
  const SLIDE_W = 1280
  const SLIDE_H = 720
  function kickerIntro(section) {
    const kicker = section.querySelector('.kicker')
    if (!kicker || reduce) return
    section.getAnimations({ subtree: true }).forEach((a) => a.cancel())
    const scale = Reveal.getScale() || 1
    const box = section.getBoundingClientRect()
    const k = kicker.getBoundingClientRect()
    const dx = SLIDE_W / 2 - (k.left + k.width / 2 - box.left) / scale
    const dy = SLIDE_H / 2 - (k.top + k.height / 2 - box.top) / scale
    const big = `translate(${dx}px, ${dy}px) scale(3)`
    kicker.animate(
      [{ transform: big, opacity: 0 }, { transform: big, opacity: 1, offset: 0.15 }, { transform: big, offset: 0.55 }, { transform: 'none' }],
      { duration: 2000, easing: 'cubic-bezier(.5,.05,.3,1)' })
    section.querySelectorAll('.rail .path, .frame > .body, .frame > .foot').forEach((el) => el.animate(
      [{ opacity: 0 }, { opacity: 0, offset: 0.75 }, { opacity: 1 }],
      { duration: 2400, easing: 'ease-out' }))
  }
  function frames() {
    return [...document.querySelectorAll('.reveal .slides iframe.embed')]
  }
  function tell(frame, message) {
    try { frame.contentWindow?.postMessage({ silta: message }, location.origin) } catch { /* not loaded yet */ }
  }
  function arrive(event) {
    const current = event.currentSlide
    const forward = !event.previousSlide || Reveal.getIndices(event.previousSlide).h < Reveal.getIndices(current).h
    if (forward && current.classList.contains('kicker-intro')) kickerIntro(current)
    frames().forEach((frame) => tell(frame, current.contains(frame) ? 'play' : 'prime'))
  }
  addEventListener('message', (event) => {
    if (event.origin !== location.origin || event.data?.silta !== 'ready?') return
    const frame = frames().find((f) => f.contentWindow === event.source)
    if (frame) tell(frame, Reveal.getCurrentSlide()?.contains(frame) ? 'play' : 'prime')
  })
  Reveal.on('slidechanged', arrive)
  if (Reveal.isReady()) arrive({ currentSlide: Reveal.getCurrentSlide() })
  else Reveal.on('ready', (event) => arrive({ currentSlide: event.currentSlide }))
})()
