export function getBaseUrl(): string {

  // Extract the hostname from the current URL
  const hostname = window.location.hostname
  const port = window.location.port
  // Check for localhost addresses and return '' if matched
  if (
    (hostname === 'localhost' ||
    hostname === '127.0.0.1' ||
    hostname === '0.0.0.0') && port === '8000'
  ) {
    return ''
  }

  // Return the current page URL enclosed in double quotes if none of the above conditions are met
  return `${window.location.origin}`
}