import { createControls } from 'botasaurus-controls'
import { useMemo } from 'react'
import { useState } from 'react'

import { EmptyScraper } from '../Empty/Empty'
import MarkdownComponent from '../MarkdownComponent/MarkdownComponent'
import ScraperSelector from '../ScraperSelector/ScraperSelector'
import { getBaseUrl } from './getBaseUrl'
import { createApiREADME } from './createApiREADME'

const ContentContainer = ({ selectedScraper, hasSingleScraper }: { selectedScraper: any, hasSingleScraper: boolean }) => {
  const baseUrl = getBaseUrl()

  const sorts = selectedScraper.sorts
  const filters = selectedScraper.filters
  const views = selectedScraper.views
  const default_sort = selectedScraper.default_sort

  // eslint-disable-next-line
  const controls = useMemo(() => createControls(selectedScraper.input_js),[selectedScraper.scraper_name])

  //@ts-ignore
  const defdata = controls.getParsedControlData(controls.getDefaultData())

  const readmeContent = createApiREADME(baseUrl, selectedScraper.scraper_name,hasSingleScraper, defdata, sorts, filters, views, default_sort, selectedScraper.route_path, selectedScraper.max_runs,
  // @ts-ignore
    window.apiBasePath ?? '',
  // @ts-ignore
    window.routeAliases[selectedScraper.scraper_name] ?? [],
    // @ts-ignore
    window.enable_cache,
  )

  return <MarkdownComponent content={readmeContent} />
}

const ScraperContainer = ({ scrapers }: { scrapers: any[] }) => {
  const [selectedScraper, setSelectedScraper] = useState(scrapers[0])
  
  const hasSingleScraper = scrapers.length <= 1
  return (
    <div>
      {hasSingleScraper ? null : (
        <ScraperSelector
          scrapers={scrapers}
          selectedScraper={selectedScraper}
          onSelectScraper={setSelectedScraper}
        />
      )}
      <ContentContainer hasSingleScraper={hasSingleScraper} selectedScraper={selectedScraper} />
    </div>
  )
}

const ApiIntegrationComponent = () => {
  // @ts-ignore
  const scrapers = window.scrapers
  if (!scrapers || scrapers.length === 0) {
    return <EmptyScraper />
  }

  return <ScraperContainer scrapers={scrapers} />
}

export default ApiIntegrationComponent