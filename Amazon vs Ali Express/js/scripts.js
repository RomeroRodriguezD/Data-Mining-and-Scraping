// Constant and function to bring the HTML structure back to the original size

const initialBodyContent = document.body.innerHTML;

 function resetStructure() {
  document.body.innerHTML = initialBodyContent;
 }

// Adapts structure to 424px viewport

const productItems = document.querySelectorAll('.product-item');

function adjustLayout() {
  var windowWidth = window.innerWidth;
  if (windowWidth <= 424) {
    var columns = document.querySelectorAll('.column');
    columns.forEach(function(column) {
      var productItems = column.querySelectorAll('.product-item');
      productItems.forEach(function(item) {
        var productDetails = item.querySelector('.product-details');
        var productImage = item.querySelector('.product-image');
        var imageContainer = item.querySelector('.image-container');

        // Removes image-container, only needed on bigger sizes.
        imageContainer.parentNode.removeChild(imageContainer);

        // Moves product image to the block display for each product
        productDetails.appendChild(productImage);
      });
    });

    // Also not needed with smaller viwwport
    var optionsBar = document.querySelector('.options-bar');
    optionsBar.parentNode.removeChild(optionsBar);
    var spacers_out  = document.querySelectorAll('.spacer');
    spacers_out.forEach(function(item){
           item.parentNode.removeChild(item);
    });

  } else {
    resetStructure();
  }
    // Trigger product names on hover.
  activateTooltips();
}

// Adjusts layout when loading and resizing
window.addEventListener('DOMContentLoaded', adjustLayout);
window.addEventListener('resize', adjustLayout);

// Trigger name tags on hover

function activateTooltips() {
  const tooltipElements = document.querySelectorAll('[data-tooltip]');
  tooltipElements.forEach(function(element) {
    const tooltipText = element.dataset.tooltip;
    const tooltip = document.createElement('div');
    tooltip.classList.add('tooltip');
    tooltip.textContent = tooltipText;
    element.addEventListener('mouseenter', function() {
        document.body.appendChild(tooltip);
        tooltip.style.top = `${event.pageY}px`;
        tooltip.style.left = `${event.pageX}px`;
        tooltip.style.display = 'block';
    });
    element.addEventListener('mouseout', function() {
        document.body.removeChild(tooltip);
    });
  });
}

activateTooltips();








