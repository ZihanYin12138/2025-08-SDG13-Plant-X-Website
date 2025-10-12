<script setup>
import { ref, onMounted, computed } from 'vue'

const BASE = 'https://ky21h193r2.execute-api.us-east-1.amazonaws.com/plantx'

// Reactive data
const clubsData = ref(null)
const loading = ref(false)
const searchQuery = ref('')
const selectedState = ref('All')
const allStates = ref(['All'])

// Pagination related
const currentPage = ref(1)
const itemsPerPage = 8

// Fetch clubs data
async function fetchClubsData(state = null) {
  loading.value = true
  try {
    let url = `${BASE}/gardening_clubs`
    if (state && state !== 'All') {
      url += `?state=${state.toLowerCase()}`
    }
    
    const response = await fetch(url, {
      headers: { Accept: 'application/json' }
    })
    if (response.ok) {
      clubsData.value = await response.json()
      console.log('Clubs data loaded successfully:', clubsData.value)
      
      // If fetching all data, update states list
      if (!state || state === 'All') {
        updateStatesList()
      }
    } else {
      console.error('Failed to fetch clubs data:', response.status)
    }
  } catch (error) {
    console.error('Error fetching clubs data:', error)
  } finally {
    loading.value = false
  }
}

// Update states list
function updateStatesList() {
  // Since API returned data doesn't have State field, we use predefined states list
  const predefinedStates = ['All', 'VIC', 'NSW', 'QLD', 'SA', 'WA', 'ACT', 'TAS', 'NT']
  allStates.value = predefinedStates
  console.log('Updated states list:', allStates.value)
}

// Filtered clubs list
const filteredClubs = computed(() => {
  if (!clubsData.value?.all_clubs) return []
  
  let filtered = clubsData.value.all_clubs
  
  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(club => 
      club.Name?.toLowerCase().includes(query) ||
      club.Contact?.toLowerCase().includes(query) ||
      club.Meetings?.toLowerCase().includes(query)
    )
  }
  
  return filtered
})

// Paginated clubs list
const paginatedClubs = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredClubs.value.slice(start, end)
})

// Total pages
const totalPages = computed(() => {
  return Math.ceil(filteredClubs.value.length / itemsPerPage)
})

// Pagination info
const paginationInfo = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage + 1
  const end = Math.min(currentPage.value * itemsPerPage, filteredClubs.value.length)
  return `${start}-${end} of ${filteredClubs.value.length} clubs`
})

// Handle state filter change
function handleStateChange() {
  currentPage.value = 1 // Reset to first page
  fetchClubsData(selectedState.value)
}

// Pagination control functions
function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

function goToPreviousPage() {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

function goToNextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

// Reset to first page when searching
function handleSearch() {
  currentPage.value = 1
}

// Open external link
function openLink(url) {
  window.open(url, '_blank', 'noopener,noreferrer')
}

// Handle page input
function handlePageInput() {
  if (currentPage.value < 1) {
    currentPage.value = 1
  } else if (currentPage.value > totalPages.value) {
    currentPage.value = totalPages.value
  }
}

// Today's meetings
const todaysMeetings = computed(() => {
  return clubsData.value?.today_clubs || []
})

onMounted(() => {
  fetchClubsData()
})
</script>


<template>
  <section class="section">
    <div class="container">
      <h2 class="title">Community Plant Clubs</h2>
    <p class="lead">Join gardening enthusiasts to share experiences and collaborate on climate-positive actions.</p>
    </div>
  </section>

  <!-- Today's Meetings -->
  <section v-if="todaysMeetings.length > 0" class="section today-meetings">
    <div class="container">
      <h3 class="section-title">Today's Meetings</h3>
      <div class="meetings-grid">
        <div v-for="meeting in todaysMeetings" :key="meeting.Name" class="meeting-card">
          <div class="meeting-info">
            <h4 class="meeting-name">{{ meeting.Name }}</h4>
            <p class="meeting-time">{{ meeting.Time }}</p>
            <p class="meeting-contact" v-if="meeting.Contact">{{ meeting.Contact }}</p>
          </div>
          <div class="meeting-status">
            <span class="status-badge scheduled">Scheduled</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Search and Filter -->
  <section class="section">
    <div class="container">
      <div class="search-filters">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            @input="handleSearch"
            type="text" 
            placeholder="Search clubs..." 
            class="search-input"
          />
          <i class="search-icon">🔍</i>
        </div>
        <div class="filter-box">
          <select v-model="selectedState" @change="handleStateChange" class="filter-select">
            <option v-for="state in allStates" :key="state" :value="state">
              {{ state === 'All' ? 'All regions' : state }}
            </option>
          </select>
        </div>
      </div>
    </div>
  </section>

  <!-- Clubs List -->
  <section class="section">
    <div class="container">
      <div v-if="loading" class="loading">
        <p>Loading clubs data...</p>
      </div>
      
      <div v-else-if="filteredClubs.length === 0" class="no-results">
        <p>No matching clubs found</p>
      </div>
      
      <div v-else class="clubs-grid">
        <div v-for="club in paginatedClubs" :key="club.Name" class="club-card">
          <div class="club-header">
            <h3 class="club-name">{{ club.Name }}</h3>
            <span class="club-state" v-if="club.State">{{ club.State }}</span>
          </div>
          
          <div class="club-details">
            <div class="detail-item" v-if="club.Meetings">
              <strong>Meeting Schedule:</strong>
              <span>{{ club.Meetings }}</span>
            </div>
            
            <div class="detail-item" v-if="club.Next_meeting">
              <strong>Next Meeting:</strong>
              <span>{{ club.Next_meeting }}</span>
            </div>
            
            <div class="detail-item" v-if="club.Contact">
              <strong>Contact:</strong>
              <span>{{ club.Contact }}</span>
            </div>
            
            <div class="detail-item" v-if="club.Location">
              <strong>Location:</strong>
              <span>{{ club.Location }}</span>
            </div>
            
            <div class="detail-item" v-if="club.Link">
              <strong>Website:</strong>
              <a :href="club.Link" target="_blank" class="club-link">{{ club.Link }}</a>
            </div>
          </div>
          
          <div class="club-status">
            <span class="status-badge" :class="{
              'scheduled': club.Meetings && club.Meetings !== 'Not Applicable',
              'not-applicable': !club.Meetings || club.Meetings === 'Not Applicable'
            }">
              {{ club.Meetings && club.Meetings !== 'Not Applicable' ? 'Scheduled' : 'Not Applicable' }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- 分页控件 -->
      <div v-if="filteredClubs.length > itemsPerPage" class="pagination">
        <div class="pagination-info">
          {{ paginationInfo }}
        </div>
        
        <div class="pagination-controls">
          <button 
            @click="goToPreviousPage" 
            :disabled="currentPage === 1"
            class="pagination-btn prev-btn"
          >
            < Prev
          </button>
          
          <span class="page-label">Page</span>
          
          <input 
            v-model.number="currentPage" 
            @change="handlePageInput"
            @keyup.enter="handlePageInput"
            type="number" 
            :min="1" 
            :max="totalPages"
            class="page-input"
          />
          
          <span class="total-pages">/ {{ totalPages }}</span>
          
          <button 
            @click="goToNextPage" 
            :disabled="currentPage === totalPages"
            class="pagination-btn next-btn"
          >
            Next >
          </button>
        </div>
      </div>
    </div>
  </section>

  <!-- Community Organizations -->
  <section class="section community-orgs">
    <div class="container">
      <h3 class="section-title">Community Organizations</h3>
      <p class="section-subtitle">Connect with leading environmental organizations making a difference</p>
      
      <div class="org-cards">
        <!-- Planet Ark -->
        <div class="org-card" @click="openLink('https://nationaltreeday.org.au/')">
          <div class="org-image">
            <img src="/src/assets/Planet Ark.png" alt="Planet Ark" onerror="this.style.display='none'">
          </div>
          <div class="org-content">
            <h4 class="org-name">Planet Ark</h4>
            <p class="org-description">Organizer of National Tree Day, Australia's largest annual community tree-planting and conservation event.</p>
            <div class="org-link">
              <span>Visit Website →</span>
            </div>
          </div>
        </div>

        <!-- Community Gardens Australia -->
        <div class="org-card" @click="openLink('https://communitygarden.org.au/about/what-we-do/')">
          <div class="org-image">
            <img src="/src/assets/Community Gardens Australia.png" alt="Community Gardens Australia" onerror="this.style.display='none'">
          </div>
          <div class="org-content">
            <h4 class="org-name">Community Gardens Australia (CGA)</h4>
            <p class="org-description">National network supporting local community gardens with resources, training, and collaboration.</p>
            <div class="org-link">
              <span>Visit Website →</span>
            </div>
          </div>
        </div>

        <!-- Heartscapes -->
        <div class="org-card" @click="openLink('https://theheartgardeningproject.org.au/')">
          <div class="org-image">
            <img src="/src/assets/Heartscapes — Melbourne Pollinator Corridor Project .webp" alt="Heartscapes" onerror="this.style.display='none'">
          </div>
          <div class="org-content">
            <h4 class="org-name">Heartscapes — Melbourne Pollinator Corridor Project</h4>
            <p class="org-description">Non-profit creating community-led street gardens in Melbourne, linking Royal Botanic Gardens to Westgate Park.</p>
            <div class="org-link">
              <span>Visit Website →</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Basic styles */
.section {
  padding: 2rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #2d5a27;
  margin-bottom: 1rem;
  text-align: center;
}

.lead {
  font-size: 1.2rem;
  color: #666;
  text-align: center !important;
  margin: 0 auto 2rem auto;
  display: block;
  max-width: 100%;
  width: 100%;
}

.section-title {
  font-size: 1.8rem;
  color: #2d5a27;
  margin-bottom: 1.5rem;
  text-align: center;
}

/* Today's meetings styles */
.today-meetings {
  background: linear-gradient(135deg, #2d5a27, #4a7c59);
  color: white;
  border-radius: 12px;
  margin: 2rem 1rem;
}

.today-meetings .section-title {
  color: white;
}

.meetings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.meeting-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meeting-name {
  color: #2d5a27;
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.meeting-time {
  color: #2d5a27;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.meeting-contact {
  color: #374151;
  font-size: 0.9rem;
}

/* Search and filter styles */
.search-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #4a7c59;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.filter-box {
  min-width: 200px;
}

.filter-select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
  transition: border-color 0.3s;
}

.filter-select:focus {
  outline: none;
  border-color: #4a7c59;
}

/* Clubs list styles */
.loading, .no-results {
  text-align: center;
  padding: 3rem;
  color: #666;
  font-size: 1.1rem;
}

.clubs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.club-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  transition: transform 0.3s, box-shadow 0.3s;
}

.club-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.club-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.club-name {
  color: #2d5a27;
  font-size: 1.3rem;
  font-weight: bold;
  margin: 0;
  flex: 1;
  margin-right: 1rem;
}

.club-state {
  background: #e8f5e8;
  color: #2d5a27;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

.club-details {
  margin-bottom: 1rem;
}

.detail-item {
  margin-bottom: 0.75rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.detail-item strong {
  color: #2d5a27;
  font-weight: 600;
  min-width: 80px;
}

.detail-item span {
  color: #374151;
  flex: 1;
}

.club-link {
  color: #4a7c59;
  text-decoration: none;
  word-break: break-all;
}

.club-link:hover {
  text-decoration: underline;
}

.club-status {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}

.status-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.scheduled {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.not-applicable {
  background: #f3f4f6;
  color: #6b7280;
}

/* Responsive design */
@media (max-width: 768px) {
  .search-filters {
    flex-direction: column;
  }
  
  .search-box, .filter-box {
    min-width: 100%;
  }
  
  .clubs-grid {
    grid-template-columns: 1fr;
  }
  
  .meeting-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .club-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .club-state {
    align-self: flex-start;
  }
}

/* Pagination styles */
.pagination {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.pagination-info {
  color: #666;
  font-size: 0.9rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #374151;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s;
  min-width: 60px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.pagination-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f9fafb;
}

.page-label {
  color: #374151;
  font-size: 0.9rem;
  font-weight: 500;
}

.page-input {
  width: 60px;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  text-align: center;
  font-size: 0.9rem;
  background: white;
  color: #374151;
  transition: border-color 0.3s;
}

.page-input:focus {
  outline: none;
  border-color: #4a7c59;
  box-shadow: 0 0 0 2px rgba(74, 124, 89, 0.1);
}

.total-pages {
  color: #374151;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Responsive pagination */
@media (max-width: 768px) {
  .pagination-controls {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
  }
  
  .pagination-btn {
    min-width: 50px;
    padding: 0.4rem 0.8rem;
  }
  
  .page-input {
    width: 50px;
    padding: 0.4rem;
  }
}

/* Community organization cards styles */
.community-orgs {
  background: #f8faf9;
  border-top: 1px solid #e5e7eb;
}

.section-subtitle {
  text-align: center;
  color: #666;
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.org-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.org-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.org-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #4a7c59;
}

.org-image {
  height: 120px;
  background: linear-gradient(135deg, #4a7c59, #2d5a27);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.org-image img {
  max-width: 120px;
  max-height: 120px;
  object-fit: contain;
}


.org-content {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  flex: 1;
  justify-content: flex-start;
}

.org-name {
  color: #2d5a27;
  font-size: 1.3rem;
  font-weight: bold;
  margin: 0 0 1rem 0;
  line-height: 1.3;
  min-height: 2.6rem;
}

.org-description {
  color: #374151;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 1rem;
  flex: 1;
  min-height: 4.5rem;
  display: flex;
  align-items: flex-start;
}


.org-link {
  color: #4a7c59;
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: color 0.3s;
  min-height: 1.5rem;
  margin-top: auto;
}

.org-card:hover .org-link {
  color: #2d5a27;
}

/* Responsive design */
@media (max-width: 768px) {
  .org-cards {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .org-card {
    margin: 0 1rem;
  }
  
  .org-name {
    font-size: 1.2rem;
  }
  
  .org-description {
    font-size: 0.9rem;
  }
}
</style>
