import Cascade from "./components/Cascade";
import CrashGallery from "./components/CrashGallery";
import CrtOverlay from "./components/CrtOverlay";
import FooterCta from "./components/FooterCta";
import Hero from "./components/Hero";
import Nav from "./components/Nav";
import Reference from "./components/Reference";
import SiteFooter from "./components/SiteFooter";
import Vibes from "./components/Vibes";

export default function App() {
  return (
    <>
      <CrtOverlay />
      <Nav />
      <main>
        <Hero />
        <CrashGallery />
        <Cascade />
        <Vibes />
        <Reference />
        <FooterCta />
      </main>
      <SiteFooter />
    </>
  );
}
