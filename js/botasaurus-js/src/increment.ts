function createIncrementer() {
    let counter = 0;
    return function() {
        counter += 1;
        return counter.toString();
    };
}

// Example usage:
export const increment = createIncrementer();


