/**
 * ExamHero.jsx
 * Master Orchestrator for ExamVault Hero Section.
 * Guarantees 100% perfect matching between exam badges & 3D images:
 * - TNPSC -> ezgif-frame-005.jpg (3D TNPSC)
 * - UPSC  -> ezgif-frame-017.jpg (3D UPSC)
 * - JEE   -> ezgif-frame-030.jpg (3D JEE)
 * - NEET  -> ezgif-frame-043.jpg (3D NEET)
 * Smooth 800ms 3D transition on click.
 */
import { useState, useRef, useEffect } from 'react'
import { examHeroData } from '../../data/examHeroData'
import HeroHUD from './HeroHUD'
import HeroCardStack from './HeroCardStack'

export default function ExamHero() {
  const [currentIndex, setCurrentIndex]   = useState(0) // 0: TNPSC, 1: UPSC, 2: JEE, 3: NEET
  const [isTransitioning, setIsTrans]   = useState(false)
  const [frameIndex, setFrameIndex]     = useState(examHeroData[0].activeFrame)
  const [hasInteracted, setHasInteracted] = useState(false)

  const animFrameReq = useRef(null)
  const activeExam = examHeroData[currentIndex]

  // Keep frameIndex strictly synced with currentIndex when not transitioning
  useEffect(() => {
    if (!isTransitioning) {
      setFrameIndex(examHeroData[currentIndex].activeFrame)
    }
  }, [currentIndex, isTransitioning])

  // Advance to next exam in cycle order (TNPSC → UPSC → JEE → NEET → TNPSC)
  const advanceCycle = () => {
    if (isTransitioning) return
    if (!hasInteracted) setHasInteracted(true)

    setIsTrans(true)
    const currentExam = examHeroData[currentIndex]
    const nextIndex   = (currentIndex + 1) % examHeroData.length
    const nextExam    = examHeroData[nextIndex]

    const startF = currentExam.activeFrame
    let endF     = nextExam.activeFrame
    if (endF <= startF) {
      endF += 50
    }

    const duration  = 850 // Smooth 850ms transition
    const startTime = performance.now()

    const step = (now) => {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const currentF = Math.floor(startF + progress * (endF - startF)) % 50
      setFrameIndex(currentF)

      if (progress < 1) {
        animFrameReq.current = requestAnimationFrame(step)
      } else {
        setCurrentIndex(nextIndex)
        setFrameIndex(nextExam.activeFrame)
        setIsTrans(false)
      }
    }

    animFrameReq.current = requestAnimationFrame(step)
  }

  // Jump directly to an exam via cycle dot click
  const jumpToIndex = (targetIndex) => {
    if (isTransitioning || targetIndex === currentIndex) return
    if (!hasInteracted) setHasInteracted(true)

    setIsTrans(true)
    const currentExam = examHeroData[currentIndex]
    const targetExam  = examHeroData[targetIndex]

    const startF = currentExam.activeFrame
    let endF     = targetExam.activeFrame
    if (endF <= startF) {
      endF += 50
    }

    const duration  = 750
    const startTime = performance.now()

    const step = (now) => {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const currentF = Math.floor(startF + progress * (endF - startF)) % 50
      setFrameIndex(currentF)

      if (progress < 1) {
        animFrameReq.current = requestAnimationFrame(step)
      } else {
        setCurrentIndex(targetIndex)
        setFrameIndex(targetExam.activeFrame)
        setIsTrans(false)
      }
    }

    animFrameReq.current = requestAnimationFrame(step)
  }

  return (
    <section className="exam-hero-container" style={{ position: 'relative', width: '100%', overflow: 'hidden', padding: '60px 0 48px', backgroundColor: 'var(--color-bg)' }}>
      <div className="container" style={{ position: 'relative', zIndex: 10 }}>
        {/* HUD Text overlay displayed above the 3D card stack */}
        <HeroHUD
          exam={activeExam}
          index={currentIndex}
          total={examHeroData.length}
          onJumpToIndex={jumpToIndex}
          hasInteracted={hasInteracted}
        />

        {/* 3D Card Stack directly below HUD text */}
        <HeroCardStack
          examOrder={examHeroData}
          currentIndex={currentIndex}
          onAdvance={advanceCycle}
          isTransitioning={isTransitioning}
          frameIndex={frameIndex}
        />
      </div>
    </section>
  )
}
