import tsStylistic from '@stylistic/eslint-plugin-ts';
import prettier from 'eslint-config-prettier';
import globals from 'globals';
import tsEslint from 'typescript-eslint';

import apify from '@apify/eslint-config/ts';

// eslint-disable-next-line import/no-default-export
export default [
    {
        ignores: ['**/dist', 'node_modules', 'coverage', 'website', '**/*.d.ts'],
    },
    ...apify,
    prettier,
    {
        languageOptions: {
            parser: tsEslint.parser,
            parserOptions: {
                project: 'tsconfig.eslint.json',
            },
            globals: {
                ...globals.browser,
                ...globals.node,
                ...globals.jest,
            },
        },
    },
    {
        plugins: {
            '@typescript-eslint': tsEslint.plugin,
            '@stylistic': tsStylistic,
        },
        rules: {
            '@typescript-eslint/no-explicit-any': 0,
            'consistent-return': 0,
            'no-use-before-define': 0,
            'no-param-reassign': 0,
            'no-void': 0,
            'import/no-extraneous-dependencies': 0,
            'import/extensions': 0,
        },
    },
    {
        files: ['test/**/*'],
        rules: {
            '@typescript-eslint/no-empty-function': 0,
            '@typescript-eslint/no-unused-vars': 0,
            'no-console': 0,
        },
    },
];
