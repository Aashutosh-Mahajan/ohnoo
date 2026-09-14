import Mascot from "./Mascot";

export default function Nav() {
  return (
    <nav className="nav">
      <a className="nav-brand" href="#top">
        <Mascot pose="neutral" size={26} />
        ohnoo
      </a>
      <div className="nav-links">
        <a className="hide-mobile" href="#crashes">crashes</a>
        <a className="hide-mobile" href="#cascade">cascade</a>
        <a className="hide-mobile" href="#vibes">vibes</a>
        <a href="#reference">man page</a>
        <a className="gh" href="https://github.com/Aashutosh-Mahajan/ohnoo" target="_blank" rel="noreferrer">
          GitHub
        </a>
      </div>
    </nav>
  );
}
