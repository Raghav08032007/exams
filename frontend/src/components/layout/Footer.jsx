import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div className="footer-brand">
          ExamVault
        </div>
        <div className="footer-links">
          <Link to="/exam/tnpsc" className="footer-link">TNPSC</Link>
          <Link to="/exam/upsc"  className="footer-link">UPSC</Link>
          <Link to="/exam/jee"   className="footer-link">JEE</Link>
          <Link to="/exam/neet"  className="footer-link">NEET</Link>
          <Link to="/textbooks"  className="footer-link">Textbooks</Link>
          <Link to="/sources"    className="footer-link">Provenance & Sources</Link>
          <Link to="/search"     className="footer-link">Search</Link>
        </div>
        <div className="footer-copy">
          © {new Date().getFullYear()} ExamVault — Searchable Question Papers Archive
        </div>
      </div>
    </footer>
  )
}
