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
})()
