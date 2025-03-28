document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const toggleButton = document.querySelector('.toggle-sidebar');
    const showSidebarButton = document.getElementById('show-sidebar');
    const contentContainer = document.querySelector('.content-container');
  
    // Collapse Sidebar
    toggleButton.addEventListener('click', function () {
      sidebar.classList.add('collapsed');
      contentContainer.classList.add('expanded');
      showSidebarButton.style.display = 'block'; // Show "Menu" button
    });
  
    // Show Sidebar
    showSidebarButton.addEventListener('click', function () {
      sidebar.classList.remove('collapsed');
      contentContainer.classList.remove('expanded');
      showSidebarButton.style.display = 'none'; // Hide "Menu" button
    });
  });
  