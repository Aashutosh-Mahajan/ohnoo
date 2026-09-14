import { useEffect, useRef, useState } from "react";

function prefersReducedMotion() {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export default function Reveal({ as: Tag = "div", className = "", style, children }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(() => prefersReducedMotion() || !("IntersectionObserver" in window));

  useEffect(() => {
    if (visible) return;
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.unobserve(el);
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -60px 0px" }
    );
    observer.observe(el);
    return () => observer.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <Tag ref={ref} className={`reveal ${visible ? "in" : ""} ${className}`.trim()} style={style}>
      {children}
    </Tag>
  );
}
