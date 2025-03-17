
// create all states
async function populateSelectOptions() {
  // Get the select element by its ID
  const selectElement = document.getElementById('id_state');

  // Clear any existing options
  selectElement.innerHTML = '';
  // Create a document fragment to improve performance
  const fragment = document.createDocumentFragment();

  const response_state = await fetch(`{% url 'main:states' %}`);

  if (!response_state.ok) {
    console.error('Network error:', response_state.statusText);
    return;
  }


  // Assuming the response is JSON and is an array of cities
  const states = await response_state.json();
  // Loop through the options array and create option elements

  states.forEach(state => {
    const option = document.createElement('option');
    option.value = state.id;      // Set the option's value attribute
    option.textContent = state.name;  // Set the visible text
    fragment.appendChild(option);
  });

  // Append the fragment containing all options to the select element at once
  selectElement.appendChild(fragment);
}


document.addEventListener('DOMContentLoaded', function() {
    const provinceSelect = document.getElementById('id_state');
    const citySelect = document.getElementById('id_town');

    provinceSelect.addEventListener('change', async function() {
        const provinceId = this.value;
        // Clear the current list of cities
        citySelect.innerHTML = '<option value="">شهر خود را انتخاب کنید</option>';

        if (provinceId) {
            try {
                // Replace with your actual API URL. It should accept a parameter (e.g., ?province=1)
                const response = await fetch(`{% url 'main:towns-by-state' %}?province=${provinceId}`);

                if (!response.ok) {
                    console.error('Network error:', response.statusText);
                    return;
                }

                // Assuming the response is JSON and is an array of cities
                const cities = await response.json();

                // Populate the city select element
                cities.forEach(city => {
                    const option = document.createElement('option');
                    option.value = city.id;       // Ensure your API returns an "id"
                    option.textContent = city.name; // And a "name" for display
                    citySelect.appendChild(option);
                });
            } catch (error) {
                console.error('Error fetching cities:', error);
            }
        }
    });
});

