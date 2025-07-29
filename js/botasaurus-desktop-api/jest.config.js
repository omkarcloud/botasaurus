require('source-map-support/register');

module.exports = {
    verbose: true,
    preset: 'ts-jest',
    testEnvironment: 'node',
    transform: {
        '^.+\\.tsx?$': [
            'ts-jest',
            {
                tsconfig: 'test/tsconfig.json',
                isolatedModules: true,
            },
        ],
    },
    testTimeout: 20_000,
    collectCoverage: true,
    coverageProvider: 'v8',
    coverageReporters: ['text', 'lcov'],
    collectCoverageFrom: ['<rootDir>/src/**/*.[jt]s'],
    maxWorkers: 3,
};
