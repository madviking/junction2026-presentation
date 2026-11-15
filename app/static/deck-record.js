// /presentation/record: the slide picker for the recorded video, then the deck without chrome.
// Rows (app/templates/_record_picker.html) can be ticked and dragged (or moved with ↑ ↓). Start puts
// the page in full screen (it needs the click), keeps only the ticked slides in the picked order,
// writes the cut to the address (?slides=a,b,c&foot=1&drills=1) and boots the deck (deck-v3.js).
// In the speaker view (?receiver, press S) the cut from the address plays straight away.
(function () {
  const params = new URLSearchParams(location.search)
  const picker = document.getElementById('record-picker')
  const list = picker.querySelector('.rp-list')
  const slides = document.querySelector('.reveal .slides')
  const sections = new Map([...slides.children].map((s) => [s.id, s]))
  const drills = document.getElementById('rp-drills')
  const foot = document.getElementById('rp-foot')
  const count = picker.querySelector('.rp-count')

  const rows = () => [...list.children]
  const box = (row) => row.querySelector('input[type=checkbox]')
  const chosen = () => rows().filter((r) => box(r).checked).map((r) => r.dataset.id)

  function update() {
    const n = chosen().length
    count.textContent = `${n} of ${rows().length} slides`
    picker.querySelectorAll('[data-start]').forEach((b) => { b.disabled = n === 0 })
  }

  // A cut from the address: its slides first, ticked and in its order; the rest after, unticked.
  function applyCut(ids) {
    const byId = new Map(rows().map((r) => [r.dataset.id, r]))
    const picked = ids.map((id) => byId.get(id)).filter(Boolean)
    if (!picked.length) return
    rows().forEach((r) => { box(r).checked = false })
    picked.forEach((r) => { box(r).checked = true; list.appendChild(r) })
    rows().filter((r) => !picked.includes(r)).forEach((r) => list.appendChild(r))
  }
  function reset() {
    rows().sort((a, b) => a.dataset.order - b.dataset.order).forEach((r) => {
      box(r).checked = r.dataset.default === '1'
      list.appendChild(r)
    })
    drills.checked = false
    foot.checked = false
    update()
  }

  if (params.get('slides')) applyCut(params.get('slides').split(','))
  drills.checked = params.get('drills') === '1'
  foot.checked = params.get('foot') === '1'
  update()

  picker.addEventListener('change', update)
  picker.addEventListener('click', (event) => {
    const pick = event.target.closest('[data-pick]')?.dataset.pick
    if (pick === 'reset') reset()
    else if (pick) { rows().forEach((r) => { box(r).checked = pick === 'all' }); update() }
    const move = event.target.closest('[data-move]')
    if (move) {
      const row = move.closest('.rp-row')
      const step = Number(move.dataset.move)
      const other = step < 0 ? row.previousElementSibling : row.nextElementSibling
      if (other) { list.insertBefore(row, step < 0 ? other : other.nextElementSibling); move.focus() }
    }
    const start = event.target.closest('[data-start]')
    if (start && !start.disabled) play(start.dataset.start === 'full')
  })
  picker.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && event.target.matches('input[type=checkbox]')) {
      event.preventDefault()
      play(true)
    }
  })

  // Drag to reorder: the dragged row follows the pointer, dropped above or below the row under it.
  let dragged = null
  list.addEventListener('dragstart', (event) => {
    dragged = event.target.closest('.rp-row')
    if (!dragged) return
    dragged.classList.add('dragging')
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', dragged.dataset.id)
  })
  list.addEventListener('dragover', (event) => {
    if (!dragged) return
    event.preventDefault()
    const over = event.target.closest('.rp-row')
    if (!over || over === dragged) return
    const box = over.getBoundingClientRect()
    list.insertBefore(dragged, event.clientY < box.top + box.height / 2 ? over : over.nextElementSibling)
  })
  list.addEventListener('dragend', () => {
    dragged?.classList.remove('dragging')
    dragged = null
  })

  function play(full) {
    const ids = chosen()
    if (!ids.length) return
    if (full && document.fullscreenEnabled) document.documentElement.requestFullscreen().catch(() => {})
    const query = new URLSearchParams({ slides: ids.join(',') })
    if (foot.checked) query.set('foot', '1')
    if (drills.checked) query.set('drills', '1')
    // Commas stay readable in the address.
    if (!params.has('receiver')) history.replaceState(null, '', `${location.pathname}?${query.toString().replace(/%2C/g, ',')}`)
    start(ids)
  }

  function start(ids) {
    document.body.classList.toggle('show-drills', drills.checked)
    document.body.classList.toggle('show-foot', foot.checked)
    sections.forEach((section) => section.remove())
    ids.forEach((id) => { if (sections.has(id)) slides.appendChild(sections.get(id)) })
    picker.remove()
    document.body.classList.add('playing')
    window.SiltaDeck.boot(true)
    hidePointer()
  }

  // The pointer hides after IDLE_MS without movement. Embedded pages (iframes) keep their own
  // pointer, so they stop taking the mouse while it is hidden; moving it gives it back.
  function hidePointer() {
    const IDLE_MS = 1500
    let timer = null
    const wake = () => {
      document.body.classList.remove('idle')
      clearTimeout(timer)
      timer = setTimeout(() => document.body.classList.add('idle'), IDLE_MS)
    }
    addEventListener('mousemove', wake)
    addEventListener('mousedown', wake)
    wake()
  }

  if (params.has('receiver')) start(chosen())
  else picker.querySelector('.rp-start').focus({ preventScroll: true })
})()
