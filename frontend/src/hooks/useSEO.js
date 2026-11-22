import { useEffect } from 'react'

/**
 * useSEO — React hook to inject title, description, and structured JSON-LD into the document head.
 */
export function useSEO({ title, description, schema }) {
  useEffect(() => {
    if (title) document.title = title

    if (description) {
      let metaDesc = document.querySelector('meta[name="description"]')
      if (!metaDesc) {
        metaDesc = document.createElement('meta')
        metaDesc.setAttribute('name', 'description')
        document.head.appendChild(metaDesc)
      }
      metaDesc.setAttribute('content', description)
    }

    if (schema) {
      const scriptId = 'seo-schema-jsonld'
      let script = document.getElementById(scriptId)
      if (!script) {
        script = document.createElement('script')
        script.id = scriptId
        script.setAttribute('type', 'application/ld+json')
        document.head.appendChild(script)
      }
      script.textContent = JSON.stringify(schema)
    }

    return () => {
      // Optional cleanup on unmount
      const script = document.getElementById('seo-schema-jsonld')
      if (script) script.remove()
    }
  }, [title, description, schema])
}
