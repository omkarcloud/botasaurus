import { EuiFormRow } from '@elastic/eui/optimize/es/components/form/form_row/form_row';

import ChooseField from '../inputs/ChooseField';

function ScraperSelector({ scrapers, selectedScraper, onSelectScraper }) {
  const options = scrapers.map(scraper => ({
    label: scraper.name, // Assuming 'scraper_name' is a unique identifier
    value: scraper.scraper_name, // The text to display in the dropdown
  }))

  const handleChange = selectedValue => {
    if(selectedValue !== null){
      const selectedScraper = scrapers.find(
        scraper => scraper.scraper_name === selectedValue
      )
      onSelectScraper(selectedScraper)
    }

  }

  return (
    <EuiFormRow
      className="pb-4"
      label="Choose Scraper"
      display="columnCompressed"
      fullWidth>
      <div className="flex flex-row-reverse">
        <ChooseField
          name={'choose-scraper'}
          value={selectedScraper.scraper_name}
          options={options}
          onChange={handleChange}
        />
      </div>
    </EuiFormRow>
  )
}

export default ScraperSelector
