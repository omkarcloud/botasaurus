import Datastore from '@seald-io/nedb';

const RETRYABLE_WRITE_ERRORS = ['EBUSY', 'EPERM', 'EACCES'];

/**
 * On Windows an antivirus, backup or indexing tool that briefly opens the
 * datafile makes nedb's append fail with EBUSY/EPERM, after nedb has already
 * changed the docs in memory. Retries the append (by default for up to 30 s)
 * before letting the error through. Other errors, such as a full disk, are
 * not retried.
 */
export function retryTransientWrites(db: Datastore, attempts = 30, delayMs = 1000) {
  const persistence: any = (db as any).persistence;
  const persistNewStateAsync = persistence.persistNewStateAsync.bind(persistence);
  persistence.persistNewStateAsync = async (newDocs: any[]) => {
    for (let attempt = 1; ; attempt++) {
      try {
        return await persistNewStateAsync(newDocs);
      } catch (error: any) {
        if (attempt >= attempts || !RETRYABLE_WRITE_ERRORS.includes(error?.code)) throw error;
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
  };
}
