let viewers = []

  function retrieveViewersFromServer() {
    fetch("/get_viewers")
      .then(response => response.json())
      .then(data => {
        viewers = data;
        displayViewers(viewers);
      })
      .catch(error => {
        console.error("Error retrieving viewers:", error);
      });
  }
  
  // Initial retrieval and display of viewers
  retrieveViewersFromServer();
  
  const ITEMS_PER_PAGE = 5;
  let currentPage = 1;
  
  // Function to display viewers in the table
  function displayViewers(viewers) {
    const viewersBody = document.getElementById("viewersBody");
    viewersBody.innerHTML = "";
  
    if(viewers.length == 0) {
        const row = `<tr>
        <td>NULL</td>
        <td>NULL</td>
        <td>NULL</td>
        <td>NULL</td>
        <td class="actions">
          <button class="btn btn-sm btn-primary edit" onclick="" diabled>Edit</button>
          <button class="btn btn-sm btn-danger delete" onclick="" disabled>Delete</button>
        </td>
      </tr>`;
      viewersBody.innerHTML += row;
    }
    
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    const paginatedViewers = viewers.slice(startIndex, endIndex);
  
    paginatedViewers.forEach(viewer => {
      const row = `<tr>
        <td>${viewer.id}</td>
        <td>${viewer.name}</td>
        <td>${viewer.email}</td>
        <td>${viewer.lastLogin}</td>
        <td class="actions">
          <button class="btn btn-sm btn-primary edit" onclick="editViewer(${viewer.id})">Edit</button>
          <button class="btn btn-sm btn-danger delete" onclick="deleteViewer(${viewer.id})">Delete</button>
        </td>
      </tr>`;
      viewersBody.innerHTML += row;
    });
    renderPagination(viewers.length);
  }
  
  // Function to render pagination
  function renderPagination(totalItems) {
    const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);
    const paginationElement = document.getElementById("pagination");
    paginationElement.innerHTML = "";
  
    for (let i = 1; i <= totalPages; i++) {
      const li = document.createElement("li");
      li.classList.add("page-item");
      li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
      if (i === currentPage) {
        li.classList.add("active");
      }
      li.addEventListener("click", function() {
        currentPage = i;
        displayViewers(viewers);
        highlightCurrentPage();
      });
      paginationElement.appendChild(li);
    }
  }
  
  // Function to highlight current page in pagination
  function highlightCurrentPage() {
    const paginationElement = document.getElementById("pagination");
    const pages = paginationElement.querySelectorAll(".page-item");
    pages.forEach(page => {
      page.classList.remove("active");
      if (parseInt(page.textContent) === currentPage) {
        page.classList.add("active");
      }
    });
  }
  
  // Function to filter viewers based on search input
  function filterViewers(searchTerm) {
    const filteredViewers = viewers.filter(viewer =>
      viewer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      viewer.email.toLowerCase().includes(searchTerm.toLowerCase())
    );
    displayViewers(filteredViewers);
  }
  
  // Function to edit viewer details
  function editViewer(id) {
    const viewer = viewers.find(v => v.id === id);
    if (viewer) {
      const newName = prompt("Enter new name:", viewer.name);
      if (newName !== null) {
        // Send AJAX request to update user's name
        fetch(`/update_user_name/${viewer.name}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ name: newName })
        })
        .then(response => {
          if (response.ok) {
            // Update the name in the viewers array
            viewer.name = newName;
            // Update the displayed viewers
            displayViewers(viewers);
          } else {
            console.error('Failed to update user name');
          }
        })
        .catch(error => {
          console.error('Error updating user name:', error);
        });
      }
    }
  }

  function deleteViewer(id) {
    const confirmation = confirm("Are you sure you want to delete this viewer?");
    const viewer = viewers.find(v => v.id === id);
    if (confirmation) {
        fetch(`/delete_user/${viewer.name}`, {
          method: 'DELETE'
        })
        .then(response => {
          if (response.ok) {
            viewers = viewers.filter(v => v.id !== id);
            displayViewers(viewers);
          } else {
            console.error('Failed to delete viewer');
          }
        })
        .catch(error => {
          console.error('Error deleting viewer:', error);
        });
    }
  }

  document.getElementById("searchInput").addEventListener("input", function() {
    const searchTerm = this.value.trim();
    filterViewers(searchTerm);
  });

  displayViewers(viewers);
  