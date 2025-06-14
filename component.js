        // Select the menu spans correctly
        let menu = document.querySelector('.menu'); // Assuming .menu is a container for .menu-span
        let menuchild = document.querySelectorAll('.menu .menu-span');
        let nav = document.querySelector('.nav');
    
        menu.addEventListener('click', function () {
            // Toggle .opened class on all menu-span elements
            menuchild.forEach(span => {
                span.classList.toggle('opened');
            });
    
            // Toggle .opened class on nav
            nav.classList.toggle('opened');
        });

        var $cont = document.querySelector('.cont');
        var $elsArr = [].slice.call(document.querySelectorAll('.el'));
        var $closeBtnsArr = [].slice.call(document.querySelectorAll('.el__close-btn'));
        
        setTimeout(function() {
          $cont.classList.remove('s--inactive');
        }, 200);
        
        $elsArr.forEach(function($el) {
          $el.addEventListener('click', function() {
            if (this.classList.contains('s--active')) return;
            $cont.classList.add('s--el-active');
            this.classList.add('s--active');
          });
        });
        
        $closeBtnsArr.forEach(function($btn) {
          $btn.addEventListener('click', function(e) {
            e.stopPropagation();
            $cont.classList.remove('s--el-active');
            document.querySelector('.el.s--active').classList.remove('s--active');
          });
        });
        
        console.clear();
        gsap.registerPlugin(ScrollTrigger);
        window.addEventListener("load", () => {
          gsap
            .timeline({
              scrollTrigger: {
                trigger: ".wrapper",
                start: "top top",
                end: "+=150%",
                pin: true,
                scrub: true
              }
            })
            .to("", {
              scale: 5, 
              rotationX: 10, 
              rotationY: 10, 
              z: 150, 
              transformOrigin: "50% 0%",
              ease: "power1.inOut"
            })    
            .to(
              ".section.hero",
              {
                scale: 1.1,
                transformOrigin: "50% 0%",
                ease: "power1.inOut"
              },
              "<"
            );
        });