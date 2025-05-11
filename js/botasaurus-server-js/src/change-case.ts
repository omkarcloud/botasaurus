// Function to convert a string to snake_case
export function snakeCase(str: string): string {
    return str
      .replace(/([a-z])([A-Z])/g, '$1_$2') // Add underscore between camelCase words
      .replace(/\s+/g, '_') // Replace spaces with underscores
      .toLowerCase(); // Convert to lowercase
  }
  
  // Function to convert a string to Capital Case
  export function capitalCase(str: string): string {
    return str
      .replace(/([a-z])([A-Z])/g, '$1 $2') // Add space between camelCase words
      .replace(/[_\s]+/g, ' ') // Replace underscores and multiple spaces with a single space
      .replace(/\b\w/g, char => char.toUpperCase()); // Capitalize the first letter of each word
  }