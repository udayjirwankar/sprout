/* =========================================================
   SLEEPY SPROUT — CURSOR INTERACTION
   ========================================================= */

(() => {
    const sprout = document.querySelector(".sleepy-sprout");

    if (!sprout) return;

    const pupils = sprout.querySelectorAll(".sleepy-sprout__pupil");
    const body = sprout.querySelector(".sleepy-sprout__body");

    if (!pupils.length || !body) return;

    let idleTimer;

    function trackCursor(event) {
        const x = (event.clientX / window.innerWidth - 0.5) * 2;
        const y = (event.clientY / window.innerHeight - 0.5) * 2;

        /* Eyes follow the cursor */
        pupils.forEach((pupil) => {
            pupil.style.transform =
                `translate(${x * 5}px, ${y * 3}px)`;
        });

        /* Body gently leans toward the cursor */
        body.style.transform =
            `rotateX(${y * -3}deg) rotateY(${x * 6}deg)`;

        /* Wake up while the mouse is moving */
        sprout.classList.remove("is-resting");

        clearTimeout(idleTimer);

        /* Go sleepy again after inactivity */
        idleTimer = setTimeout(() => {
            sprout.classList.add("is-resting");
        }, 1800);
    }

    window.addEventListener("mousemove", trackCursor, {
        passive: true
    });

    /* Start in sleepy mode */
    sprout.classList.add("is-resting");
})();
