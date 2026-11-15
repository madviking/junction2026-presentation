// Deck v3: reveal.js setup and the drill-in sheets (chips in each slide's foot).
// One sheet open at a time; Esc, the scrim or × closes it; changing slide closes it too.
// /presentation/record (body[data-record]) waits for its slide picker (deck-record.js), which calls
// SiltaDeck.boot(true): no arrows, page numbers, progress bar, overview, help or "next" hint.
(function () {
  const RECORD = {
    controls: false, progress: false, slideNumber: false, hash: false, overview: false, help: false,
    margin: 0, // slides fill the screen's width; a 16:10 screen keeps bars only above and below
    scrollActivationWidth: null, // never switch to reveal's phone scroll view, whatever the window size
    hideInactiveCursor: false, // deck-record.js hides the pointer, also over embedded pages
  }
  function boot(record) {
    Reveal.initialize({
      hash: true, slideNumber: 'c/t', width: 1280, height: 720, margin: 0.04,
      center: false, transition: 'fade', transitionSpeed: 'fast', plugins: [RevealNotes],
      ...(record ? RECORD : {}),
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
    if (!record) nextHint()
    arrivals()

    function nextHint() {
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
    }

    function arrivals() {
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
        // Cancelling also stops the slide's own CSS build-ups (cards); .intro-running starts them again
        // after the intro (deck-v3.css). Cleared when the slide is left (arrive).
        section.classList.add('intro-running')
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
      // Film slides (video cut): the clip plays from the start when its slide is shown, and stops when it
      // is left. When it ends, the deck fades on to the next slide, slower than a keypress would.
      const filmVideos = [...document.querySelectorAll('.reveal .slides video.film')]
      function films(current) {
        filmVideos.forEach((video) => {
          const overlay = video.parentElement.querySelector('.film-overlay')
          overlay?.classList.remove('rolling')
          if (current.contains(video)) {
            video.currentTime = 0
            video.play().catch(() => {})
            if (overlay) { void overlay.offsetWidth; overlay.classList.add('rolling') } // restart the lower third
          } else video.pause()
        })
      }
      filmVideos.forEach((video) => video.addEventListener('ended', () => {
        const current = Reveal.getCurrentSlide()
        if (!current?.contains(video) || Reveal.isLastSlide()) return
        if (current.dataset.exit === 'black') { throughBlack(); return }
        Reveal.configure({ transitionSpeed: 'slow' })
        Reveal.next()
        setTimeout(() => Reveal.configure({ transitionSpeed: 'fast' }), 1300)
      }))

      // data-exit="black" (every film slide unless its `exit` says otherwise): moving on, by the clip ending or by a key, fades
      // the screen slowly to black, changes slide under it, then fades in from black. Backwards stays plain.
      const FADE_MS = 1100
      const HOLD_MS = 350
      let curtain = null
      let fading = false
      function throughBlack() {
        if (fading || Reveal.isLastSlide()) return
        fading = true
        if (!curtain) {
          curtain = document.createElement('div')
          curtain.className = 'curtain'
          curtain.style.setProperty('--fade', `${FADE_MS}ms`)
          document.body.appendChild(curtain)
          void curtain.offsetWidth
        }
        curtain.classList.add('on')
        setTimeout(() => {
          Reveal.next()
          setTimeout(() => {
            curtain.classList.remove('on')
            setTimeout(() => { fading = false }, FADE_MS)
          }, HOLD_MS)
        }, FADE_MS)
      }
      // Capture phase on window: runs before reveal's own keyboard handler (as the sheets' handler does).
      addEventListener('keydown', (event) => {
        if (!['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'n', 'N', 'Enter'].includes(event.key)) return
        if (event.key === ' ' && event.shiftKey) return
        if (!fading && Reveal.getCurrentSlide()?.dataset.exit !== 'black') return
        event.preventDefault()
        event.stopPropagation()
        throughBlack()
      }, true)

      // The gap bars: each relative drop counts up from 0 while its bars grow (CSS), on every arrival.
      function countUp(section, introDelay) {
        section.querySelectorAll('.stage .gapbar-rel').forEach((el, i) => {
          const final = el.dataset.final ?? (el.dataset.final = el.textContent)
          const match = final.match(/^(\D*)(\d+)(.*)$/)
          if (!match || reduce) return
          const [, pre, num, post] = match
          const delay = introDelay + 150 + i * 120
          const duration = 900
          el.textContent = `${pre}0${post}`
          const t0 = performance.now() + delay
          const step = (now) => {
            const k = Math.min(1, Math.max(0, (now - t0) / duration))
            el.textContent = `${pre}${Math.round(Number(num) * (1 - (1 - k) ** 3))}${post}`
            if (k < 1) requestAnimationFrame(step)
          }
          requestAnimationFrame(step)
        })
      }
      // Screen reel (.reel): the strip is copied twice so it can loop without a seam (its first screen
      // comes round again exactly where it started). It starts once the kicker intro has opened the slide.
      const REEL_PX_PER_S = 900
      // Both versions: the reel starts at REEL_PX_PER_S and slows gradually towards REEL_END_PX_PER_S
      // (half the gap closes every REEL_EASE_S seconds), then keeps running at that pace while shown.
      const REEL_END_PX_PER_S = 110
      const REEL_EASE_S = 2.2
      function coast(track, loop, current, delay) {
        const run = (track.dataset.run = String(Number(track.dataset.run || 0) + 1))
        const k = Math.LN2 / REEL_EASE_S
        let x = 0
        const t0 = performance.now() + delay // starts once the slide's intro has shown it
        let last = t0
        const step = (now) => {
          if (track.dataset.run !== run || Reveal.getCurrentSlide() !== current) { track.style.transform = ''; return }
          if (now < t0) { requestAnimationFrame(step); return }
          const t = (now - t0) / 1000
          const v = REEL_END_PX_PER_S + (REEL_PX_PER_S - REEL_END_PX_PER_S) * Math.exp(-k * t)
          x = (x + v * (now - last) / 1000) % loop
          last = now
          track.style.transform = `translateX(${-x}px)`
          requestAnimationFrame(step)
        }
        requestAnimationFrame(step)
      }
      async function reels(current, introDelay) {
        document.querySelectorAll('.reel-track').forEach((track) => track.getAnimations().forEach((a) => a.cancel()))
        const track = current.querySelector('.reel-track')
        if (!track || reduce) return
        const count = Number(track.dataset.count || (track.dataset.count = track.children.length))
        if (track.children.length === count) {
          const originals = [...track.children]
          for (let copy = 0; copy < 2; copy++) originals.forEach((img) => {
            const clone = img.cloneNode()
            clone.setAttribute('aria-hidden', 'true')
            track.appendChild(clone)
          })
        }
        // Widths need every screen loaded (img.decode() can hang in some browsers, so wait on load).
        await Promise.all([...track.querySelectorAll('img')].map((img) => img.complete || new Promise((done) => {
          img.addEventListener('load', done, { once: true })
          img.addEventListener('error', done, { once: true })
        })))
        if (Reveal.getCurrentSlide() !== current) return
        const loop = track.children[count].offsetLeft - track.children[0].offsetLeft
        coast(track, loop, current, introDelay)
      }
      // data-animate="words" (intro slides in the video cut): the line rises in word by word, with a pause
      // after each sentence (longer before the <b> finding); numbers count up as their word appears, then
      // the finding is highlighted (CSS). Replays on every arrival.
      const WORD_MS = 75
      const SENTENCE_PAUSE_MS = 650
      function wordsIn(section) {
        const line = section.querySelector('.intro-line')
        if (!line || reduce) return
        if (!line.dataset.split) {
          line.dataset.split = '1'
          const split = (node) => [...node.childNodes].forEach((child) => {
            if (child.nodeType === Node.ELEMENT_NODE) { split(child); return }
            if (child.nodeType !== Node.TEXT_NODE) return
            const frag = document.createDocumentFragment()
            child.textContent.split(/(\s+)/).forEach((part) => {
              if (!part) return
              if (/^\s+$/.test(part)) { frag.append(part); return }
              const w = document.createElement('span')
              w.className = 'w'
              w.textContent = part
              frag.append(w)
            })
            child.replaceWith(frag)
          })
          split(line)
        }
        // With a title (CSS rises it in after the kicker) the line waits until the title is in.
        let t = section.querySelector('.intro-title') ? 1500 : 500
        let prev = null
        line.querySelectorAll('.w').forEach((w) => {
          if (prev && /[.!?:]$/.test(prev.textContent)) t += SENTENCE_PAUSE_MS
          if (prev && !prev.closest('b') && w.closest('b')) t += SENTENCE_PAUSE_MS / 2
          w.style.setProperty('--d', `${t}ms`)
          const m = w.textContent.match(/^(\D*)(\d+)(\D*)$/)
          if (m) {
            const final = w.dataset.final ?? (w.dataset.final = w.textContent)
            const [, pre, num, post] = final.match(/^(\D*)(\d+)(\D*)$/)
            w.textContent = `${pre}0${post}`
            const t0 = performance.now() + t
            const step = (now) => {
              const k = Math.min(1, Math.max(0, (now - t0) / 900))
              w.textContent = `${pre}${Math.round(Number(num) * (1 - (1 - k) ** 3))}${post}`
              if (k < 1) requestAnimationFrame(step)
            }
            requestAnimationFrame(step)
          }
          t += WORD_MS
          prev = w
        })
        line.querySelectorAll('b').forEach((b) => b.style.setProperty('--hl', `${t + 300}ms`))
        section.classList.remove('words-in')
        void section.offsetWidth // restart the CSS build-up
        section.classList.add('words-in')
      }
      function arrive(event) {
        const current = event.currentSlide
        document.querySelectorAll('.intro-running').forEach((el) => { if (el !== current) el.classList.remove('intro-running') })
        const forward = !event.previousSlide || Reveal.getIndices(event.previousSlide).h < Reveal.getIndices(current).h
        const intro = forward && current.classList.contains('kicker-intro') && !reduce
        if (intro) kickerIntro(current)
        reels(current, intro ? 1500 : 300)
        frames().forEach((frame) => tell(frame, current.contains(frame) ? 'play' : 'prime'))
        films(current)
        countUp(current, intro ? 2000 : 0)
        if (current.dataset.animate === 'words') wordsIn(current)
      }
      addEventListener('message', (event) => {
        if (event.origin !== location.origin || event.data?.silta !== 'ready?') return
        const frame = frames().find((f) => f.contentWindow === event.source)
        if (frame) tell(frame, Reveal.getCurrentSlide()?.contains(frame) ? 'play' : 'prime')
      })
      Reveal.on('slidechanged', arrive)
      if (Reveal.isReady()) arrive({ currentSlide: Reveal.getCurrentSlide() })
      else Reveal.on('ready', (event) => arrive({ currentSlide: event.currentSlide }))
    }
  }

  if (document.body.hasAttribute('data-record')) window.SiltaDeck = { boot }
  else boot(false)
})()
