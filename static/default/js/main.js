
$(window).scroll(function(){
    if ($(this).scrollTop() > 1) {
       $('nav').addClass('scrolled');
    } else {
       $('nav').removeClass('scrolled');
    }
});



$(function() {
   $(".open").on("click", function(e) {
     $("nav ul").toggleClass("active");
     e.stopPropagation()
   });

   $(document).on("click", function(e) {
       if ($(e.target).is("nav ul") === false) {
         $("nav ul").removeClass("active");
         $(".close").removeClass("active");
       }
     });

   $(".close").on("click", function(e) {
       $("nav ul").removeClass("active");
       $(".close").removeClass("active");
       e.stopPropagation()
   });
 
});



AOS.init();




$(window).on('load', function () {
  $('.loading').addClass('scale').fadeOut(200);
}) 







const sections = document.querySelectorAll("section[id]");

window.addEventListener("scroll", navHighlighter);

function navHighlighter() {
  
  let scrollY = window.pageYOffset;
  

  sections.forEach(current => {
    const sectionHeight = current.offsetHeight;

    const sectionTop = (current.getBoundingClientRect().top + window.pageYOffset) - 150;
    sectionId = current.getAttribute("id");
    
    
    if (
      scrollY > sectionTop &&
      scrollY <= sectionTop + sectionHeight
    ){
      document.querySelector(".w-nav a[href*=" + sectionId + "]").classList.add("active");

    } else {
      document.querySelector(".w-nav a[href*=" + sectionId + "]").classList.remove("active");
      
    }
  });
}