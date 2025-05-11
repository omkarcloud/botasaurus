import {EuiEmptyPrompt, } from '@elastic/eui/optimize/es/components/empty_prompt/empty_prompt';
import { EuiLink } from '@elastic/eui/optimize/es/components/link/link';
import { EuiImage } from '@elastic/eui/optimize/es/components/image/image';

import { getPublicAsset } from '../../utils/missc'

export const EmptyScraper = () => {
  return (
    <div  style={{ padding: '80px 0', textAlign: 'center' }}>
      <EuiEmptyPrompt
        icon={
          <EuiImage
            style={{ maxWidth: '100px', margin: 'auto' }}
            size="fullWidth"
            src={getPublicAsset('icon-256x256.png')}
            alt=""
          />
        }
        body={
          <p>
            Learn how to add scrapers by reading the Botasaurus docs
            <EuiLink
              target={'_blank'}
              href={'https://github.com/omkarcloud/botasaurus/'}>
              here
            </EuiLink>
            .
          </p>
        }
        color="subdued"
        layout="vertical"
        title={<h2>Add Scraper</h2>}
        titleSize="m"
      />
    </div>
  )
}
