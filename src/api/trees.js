/**
 * Search for trees within specified radius
 */
export async function searchTrees(params) {
    try {
      const response = await fetch('https://ky21h193r2.execute-api.us-east-1.amazonaws.com/test/TreeLocator', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(params)
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Failed to search trees:', error)
      throw new Error(error.message || 'Error occurred while searching trees')
    }
  }
  
  /**
   * Get tree details by ID
   */
  export async function getTreeById(comId) {
    try {
      const url = new URL('https://ky21h193r2.execute-api.us-east-1.amazonaws.com/test/TreeLocator')
      url.searchParams.set('com_id', comId)
      
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Failed to get tree details:', error)
      throw new Error(error.message || 'Error occurred while getting tree details')
    }
  }