// definition of all the functions


// title animation starts later

setTimeout(() => {
  const title = document.getElementsByClassName('header-banner__h1');
  console.log(title[0]);
  title[0].innerHTML = 'CONTEXT';
}, 1500);


// smooth scrolling
// scroll-effect
const scrolling = new SmoothScroll('a[href*="#__"]',
  {
    speed: 600,
    updateUrl: false,
  });

const scrollButton = document.getElementById('scrolling-button');
scrollButton.addEventListener('click', () => {
  const height = (window.innerHeight * 0.85) + (window.innerWidth * 0.02);
  scrolling.animateScroll(height);
})

// navigation event listeners
let boolContentVisible = false;
const textContainer = document.getElementsByClassName('pages-content')[0];
const gridContainer = document.getElementsByClassName('rig')[0];
const navItems = document.getElementsByClassName('rig-cell');
function navigationContent() {
  for (let i = 0; i < navItems.length; i++) {
    navItems[i].addEventListener('click', function () {
      const text = document.getElementById('pages-content__' + navItems[i].id);
      gridContainer.style.setProperty('position', boolContentVisible ? 'relative' : 'absolute');
      gridContainer.setAttribute('class', 'rig slide-out');
      textContainer.style.setProperty('display', boolContentVisible ? 'none' : 'inline-table');
      text.style.setProperty('opacity', boolContentVisible ? 0 : 1);
      text.style.setProperty('display', boolContentVisible ? 'none' : 'block');
      boolContentVisible = !boolContentVisible;
      AOS.refreshHard();
    });
  }
}

// dropdown language picker

// initialize variables
const sum = $('summary.summary'),
  det = $('details.details'),
  sel = $('select'),
  btn = $('button.opt');

let html = $('button.selected').html();
let btnsVal = Array.prototype.slice.call(btn).map((item, index) => {
  let val = item.attributes['data-lang'].nodeValue;
  let selected = item.attributes.class.nodeValue.includes('selected') ? 'true' : 'false';
  return { val: val, selected: selected };
});

// lopp to create <option /> with correct values of languages
for (let i = 0; i < btnsVal.length; i++) {
  if (btnsVal[i].selected === 'true') {
    sel.append(`<option selected data-lang="${btnsVal[i].val}">${btnsVal[i].val}</option>`)
  }
  else {
    sel.append(`<option data-lang="${btnsVal[i].val}">${btnsVal[i].val}</option>`)
  }
}
//this cause <summary /> value always be the same as in .selected button
sum.html(html);

//function to handle mouseclicking 
btn.click(function () {
  let x = $('select option');
  let atr = $(this).attr('data-lang');
  let html = $(this).html();
  $("[data-localize]").localize("language", { language: atr });

  $(this).addClass('selected');
  btn.not($(this)).removeClass('selected')
  det.removeAttr('open');
  sum.html(html);
  x.each((i, el) => {
    if (el.attributes['data-lang'].nodeValue === atr) {
      el.selected = true;
    }
    else {
      el.selected = false;
    }
  })
})

window.addEventListener('click', function (e) {
  if (det[0].open && e.target.id !== 'language-picker') {
    det.removeAttr('open');
  }
})

// translate
// document.getElementsByClassName('language__select')[0].addEventListener('change', function(e) {
//   $("[data-localize]").localize("language", { language: e.target.value });
// });

function translate() {
  $("[data-localize]").localize("language", { language: "en" });
}


/**
 * jQuery Expanding Grid plugin.
 *
 * By Dan Boulet - https://danboulet.com
 */
(function ($, window, document) {

  // Enable strict mode
  "use strict";

  /**
   * Return the last element in the current row of a grid layout.
   */
  var getLastSiblingInRow = function (element) {
    var candidate = element,
      elementTop = element.offsetTop;

    // Loop through the element’s next siblings and look for the first one which
    // is positioned further down the page.
    while (candidate.nextElementSibling !== null) {
      if (candidate.nextElementSibling.offsetTop > elementTop) {
        return candidate;
      }
      candidate = candidate.nextElementSibling;
    }
    return candidate;
  };

  /**
   * Calculate the distance that we need to scroll the page to bring a
   * section, defined as the area between the top and bottom, into view.
   */
  var calculatePageScrollDistance = function (top, bottom) {
    var windowScrollDistance = $(window).scrollTop(),
      windowHeight = $(window).height(),
      scrollDistanceToTop,
      scrollDistanceToBottom;

    // Scroll to the top of the section if the we are already scrolled past it.
    if (windowScrollDistance >= top) {
      return top - windowScrollDistance;
    }
    // Do nothing if there is enough space to show the section without having to scroll.
    else if ((windowScrollDistance + windowHeight) >= bottom) {
      return 0;
    }
    else {
      // Find the maximum distance we can scroll without passing the top of the section.
      scrollDistanceToTop = top - windowScrollDistance;
      // Find the distance we need to scroll to reveal the entire section.
      scrollDistanceToBottom = bottom - (windowScrollDistance + windowHeight);

      return Math.min(scrollDistanceToTop, scrollDistanceToBottom);
    }
  };

  /**
   * Create the expanding preview grid.
   */
  var expandingGrid = function (context, options) {
    var defaults = {
      animationDuration: 250,
      linksSelector: '.links a',
      expandingAreaSelector: '.expanding-container',
      closeButtonMarkup: '<a href="#" class="close-button">Close</a>',
      spacerMarkup: '<span class="spacer" aria-hidden="true"/>',
      elementActiveClass: 'active',
      elementExpandedClass: 'expanded',
      onExpandBefore: false,
      onExpandAfter: false
    };

    var settings = $.extend({}, defaults, options);

    var isExpanded = false;
    var activeLink = false;
    var activeExpandedArea = false;
    var activeExpandedAreaTop = false;
    var activeExpandedAreaHeight = false;
    var lastItemInActiveRow = false;
    var activeRowChanged = false;
    var checkExpandedAreaResize = false;
    var $links = $(settings.linksSelector, context);
    var $expandingAreas = $(settings.expandingAreaSelector, context);
    var $closeButton = $(settings.closeButtonMarkup);
    var $spacer = $(settings.spacerMarkup);
    var $secondarySpacer = $spacer.clone();

    /**
     * Scroll a section of the page into view, using animation.
     */
    var scrollSectionIntoView = function (top, bottom, duration, callback) {
      var animate;
      var scroll = 0;
      var distance = calculatePageScrollDistance(top, bottom);
      var windowScrollDistance = $(window).scrollTop();
      var timeLeft;

      // Set default duration.
      duration = (typeof duration === 'undefined') ? settings.animationDuration : duration;
      timeLeft = duration;

      var start = new Date().getTime();
      var last = start;
      var tick = function () {
        timeLeft = Math.max(duration - (new Date() - start), 0);

        var x = (timeLeft === 0 || distance === 0) ? 0 : ((new Date() - last) / timeLeft * distance);
        var diff = (distance > 0 ? Math.min(x, distance) : Math.max(x, distance));
        distance = distance - diff;
        scroll += diff;
        window.scrollTo(0, windowScrollDistance + scroll);

        last = new Date().getTime();

        if (last - start <= duration) {
          animate = (window.requestAnimationFrame && requestAnimationFrame(tick)) || setTimeout(tick, 16);
        }
        else {
          if (typeof callback === 'function') {
            callback();
          }
        }
      };

      tick();
    };

    // Process the links.
    $links.each(function () {
      var $this = $(this);
      var targetId = $this.attr('href').match(/#([^\?]+)/)[1];
      var target = document.getElementById(targetId);

      if (target) {
        $this.click(function (event) {
          var clickedLink = this;
          var scrollTargetOffset;
          var closeButtonAnimationDelay;

          event.preventDefault();

          // Is this link already expanded?
          if (isExpanded && activeLink === clickedLink) {
            // Close it.
            $closeButton.click();
            setTimeout(() => AOS.refreshHard(), 300);
          }
          // Otherwise, expand it.
          else {
            $links.removeClass(settings.elementActiveClass).filter($this).addClass(settings.elementActiveClass).parent('li').each(function () {
              var lastSibling = getLastSiblingInRow(this);
              activeRowChanged = lastSibling !== lastItemInActiveRow;
              if (activeRowChanged) {
                lastItemInActiveRow = lastSibling;
              }
              // If we are changing rows, replace spacer with secondary spacer.
              if (isExpanded && activeRowChanged) {
                $secondarySpacer.height($spacer.height());
                $spacer.height(0).replaceWith($secondarySpacer);
              }
              $(lastItemInActiveRow).after($spacer);
            });
            if (isExpanded && activeRowChanged) {
              $secondarySpacer.animate({ height: 0 }, settings.animationDuration, function () {
                $(this).detach();
              });
              $closeButton.removeClass(settings.elementActiveClass).hide();
            }
            scrollTargetOffset = ($secondarySpacer.position().top < $spacer.position().top ? $secondarySpacer.height() : 0);
            activeExpandedAreaTop = ($spacer.position().top - scrollTargetOffset);
            $expandingAreas.removeClass(settings.elementExpandedClass).hide().filter(target).each(function () {
              var $this = $(this);
              var autoHeight = $this.height();
              var autoOuterHeight = $this.outerHeight();
              var initialHeight = (isExpanded && activeExpandedAreaHeight && (activeRowChanged === false)) ? activeExpandedAreaHeight : 0;

              stopExpandedAreaMonitor();

              $spacer.animate({ height: autoHeight + 'px' }, settings.animationDuration);

              $this.css({
                height: initialHeight + 'px',
                position: 'absolute',
                left: 0,
                top: $spacer.position().top + 'px'
              }).show(0, function () {
                // Callback.
                if (typeof settings.onExpandBefore === 'function') {
                  settings.onExpandBefore.call(this);
                }
              }).animate({
                height: autoHeight + 'px',
                top: activeExpandedAreaTop + 'px'
              }, settings.animationDuration, function () {
                $this.css({ height: 'auto' }).addClass(settings.elementExpandedClass);

                // Set a timer to monitor changes to expanded area’s height.
                activeExpandedAreaHeight = $this.height();
                checkExpandedAreaResize = setInterval(function () {
                  var activeExpandedAreaNewHeight = $this.height();
                  if (activeExpandedAreaNewHeight !== activeExpandedAreaHeight) {
                    activeExpandedAreaHeight = activeExpandedAreaNewHeight;
                    syncExpandedAreaWithSpacer();
                  }
                }, 1000);

                // Callback.
                if (typeof settings.onExpandAfter === 'function') {
                  settings.onExpandAfter.call(this);
                }
              });

              // Scroll the page to bring the active link and preview into view.
              var scrollTargetTop = $(clickedLink).offset().top - scrollTargetOffset;
              var scrollTargetBottom = $this.offset().top + autoOuterHeight + 20 - scrollTargetOffset;
              scrollSectionIntoView(scrollTargetTop, scrollTargetBottom);
            });

            // Activate close button.
            closeButtonAnimationDelay = (isExpanded && activeRowChanged && ($this.parent().index() > $(activeLink).parent().index())) ? settings.animationDuration : (settings.animationDuration / 4);
            $closeButton.css({
              position: 'absolute',
              right: 0,
              top: activeExpandedAreaTop + 'px'
            }).delay(closeButtonAnimationDelay).fadeIn(settings.animationDuration, function () {
              $(this).addClass(settings.elementActiveClass);
            });

            // Set global variables.
            activeLink = this;
            activeExpandedArea = target;
            isExpanded = true;
          }
        });
      }
    });

    // Process the close button.
    $closeButton.appendTo(context).hide().click(function (event) {
      var $activeLink = $(activeLink);
      var activeLinkTopOffset = $activeLink.offset().top;
      var activeLinkBottomOffset = activeLinkTopOffset + $activeLink.outerHeight();

      event.preventDefault();

      // DOM manipulation and animations.
      $links.removeClass(settings.elementActiveClass);
      $expandingAreas.slideUp(settings.animationDuration).removeClass(settings.elementExpandedClass);
      $closeButton.removeClass('active').hide();
      $spacer.animate({ height: 0 }, settings.animationDuration, function () {
        $spacer.detach();
      });

      // Scroll the page to bring the active link into view.
      scrollSectionIntoView(activeLinkTopOffset, activeLinkBottomOffset);

      stopExpandedAreaMonitor();

      // Reset global variables.
      isExpanded = false;
      activeLink = false;
      activeExpandedArea = false;
    });

    /**
     * Stop monitoring size of expanded area.
     */
    var stopExpandedAreaMonitor = function () {
      if (checkExpandedAreaResize) {
        clearInterval(checkExpandedAreaResize);
      }
    };

    /**
     * Match preview and spacer in height and position.
     */
    var syncExpandedAreaWithSpacer = function () {
      if (activeExpandedArea && isExpanded) {
        $spacer.height($(activeExpandedArea).height());
        activeExpandedAreaTop = $spacer.position().top;
        $closeButton.add(activeExpandedArea).css({ top: activeExpandedAreaTop + 'px' });
      }
    };

    /**
     * Place spacer in proper position within grid.
     */
    var positionSpacer = function () {
      var lastSibling;
      if (activeLink && lastItemInActiveRow && isExpanded) {
        // Remove spacer.
        $spacer.detach();
        lastSibling = getLastSiblingInRow($(activeLink).parent()[0]);
        // Reposition spacer, if necessary.
        if (lastItemInActiveRow !== lastSibling) {
          console.log(lastSibling);
          lastItemInActiveRow = lastSibling;
        }
        // Restore spacer.
        $(lastItemInActiveRow).after($spacer);
      }
    };

    // React to window resize.
    $(window).resize(function () {
      if (isExpanded) {
        positionSpacer();
        syncExpandedAreaWithSpacer();
      }
    });
  };

  // Create the jQuery plugin.
  $.fn.expandingGrid = function (options) {
    return this.each(function () {
      expandingGrid(this, options);
    });
  };

})(jQuery, window, document);

$(document).ready(function () {
  $('.expanding-grid').expandingGrid();
});


// appear on scroll
AOS.init({
  offset: 30,
});

translate();
navigationContent();