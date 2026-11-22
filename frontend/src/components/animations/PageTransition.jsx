/**
 * PageTransition — Framer Motion page wrapper for route-level transitions.
 * Gives the feeling of "moving deeper into the archive" as you navigate.
 * Automatically degrades to a simple opacity fade if prefers-reduced-motion is set.
 */
import { motion } from 'framer-motion'
import { useReducedMotion } from '../../hooks/useReducedMotion'

const motionVariants = {
  initial: { opacity: 0, y: 18, scale: 0.99 },
  animate: { opacity: 1, y: 0,  scale: 1    },
  exit:    { opacity: 0, y: -12, scale: 1.005 },
}

const reducedVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit:    { opacity: 0 },
}

const motionTransition   = { duration: 0.32, ease: [0.22, 1, 0.36, 1] }
const reducedTransition  = { duration: 0.15, ease: 'linear' }

export default function PageTransition({ children }) {
  const reduced = useReducedMotion()

  return (
    <motion.div
      variants={reduced ? reducedVariants : motionVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={reduced ? reducedTransition : motionTransition}
      style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}
    >
      {children}
    </motion.div>
  )
}
