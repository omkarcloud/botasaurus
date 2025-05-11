import { EuiMarkdownFormat } from '@elastic/eui/optimize/es/components/markdown_editor/markdown_format';
import { getDefaultEuiMarkdownPlugins } from '@elastic/eui/optimize/es/components/markdown_editor/plugins/markdown_default_plugins/plugins';

const MarkdownComponent = ({ content, use_target_blank = false }) => {
  if (use_target_blank) {
    const { processingPlugins, parsingPlugins } = getDefaultEuiMarkdownPlugins({
      processingConfig: {
        linkProps: { target: '_blank' },
      },
    });

    return (
      <EuiMarkdownFormat
        processingPluginList={processingPlugins}
        parsingPluginList={parsingPlugins}
      >
        {content}
      </EuiMarkdownFormat>
    );
  }
  return <EuiMarkdownFormat>{content}</EuiMarkdownFormat>;
};

export default MarkdownComponent;
