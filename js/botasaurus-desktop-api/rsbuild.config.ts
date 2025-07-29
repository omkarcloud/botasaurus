import { defineConfig } from '@rsbuild/core';
import { pluginNodePolyfill } from '@rsbuild/plugin-node-polyfill';

import { version } from './package.json';

// eslint-disable-next-line import/no-default-export
export default defineConfig({
    source: {
        entry: {
            Omkar: './src/index.ts',
        },
        define: {
            VERSION: JSON.stringify(version),
            BROWSER_BUILD: true,
        },
    },
    output: {
        distPath: { js: '.' },
        filename: { js: 'bundle.js' },
        // filename: { js: '[name].js' },
        target: 'web',
        cleanDistPath: false,
        sourceMap: true,
        minify: {
            jsOptions: {
                minimizerOptions: {
                    mangle: false,
                },
            },
        },
    },
    tools: {
        htmlPlugin: false,
        rspack(config) {
            config.output = {
                ...config.output,
                library: {
                    type: 'umd', // or 'umd', 'commonjs', etc.
                    name: 'Omkar',
                },
                globalObject: 'this',
            };
            config.optimization = {
                ...config.optimization,
                providedExports: false,
                usedExports: false,
                splitChunks: false,
                minimize: false,
            };
            config.devtool = 'source-map';
        },
    },
    // mode: 'production',
    mode: 'development',
    plugins: [pluginNodePolyfill()],
});
