import type { Config } from '@jest/types';

export default async (): Promise<Config.InitialOptions> => ({
    verbose: true,
    preset: 'ts-jest',
    testEnvironment: 'node',
    testRunner: 'jest-circus/runner',
    testTimeout: 40_000,
    collectCoverage: true,
    collectCoverageFrom: [
        '**/src/**/*.ts',
        '**/src/**/*.js',
        '!**/node_modules/**',
    ],
    maxWorkers: 3,
    globals: {
        'ts-jest': {
            tsconfig: '<rootDir>/test/tsconfig.json',
        },
    },
});
