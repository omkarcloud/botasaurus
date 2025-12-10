// Using AWS SDK v3 modular imports for smallest bundle size
import { S3Client, type ObjectCannedACL } from '@aws-sdk/client-s3'
import { Upload } from '@aws-sdk/lib-storage'
import { createReadStream } from 'fs'
import { basename } from 'path'

export interface AwsCredentials {
  accessKeyId: string
  secretAccessKey: string
  region: string
}

export interface UploadOptions {
  /** Local file path to upload */
  filePath: string
  /** S3 bucket name */
  bucket: string
  /** AWS credentials */
  credentials: AwsCredentials
  /** Optional: Custom key (path) in S3. Defaults to the filename */
  key?: string
  /** Optional: Content type. Auto-detected if not provided */
  contentType?: string
  /** Optional: ACL for the object. Defaults to 'public-read'. Set to null for ACL-disabled buckets */
  acl?: ObjectCannedACL | null
}

export interface UploadResult {
  bucket: string
  key: string
  location: string
}

/**
 * Uploads a local file to S3 (automatically uses multipart upload for large files)
 */
export async function uploadToS3(options: UploadOptions): Promise<UploadResult> {
  const { filePath, bucket, credentials, key, contentType, acl = 'public-read' } = options

  const s3Client = new S3Client({
    region: credentials.region,
    credentials: {
      accessKeyId: credentials.accessKeyId,
      secretAccessKey: credentials.secretAccessKey,
    },
  })

  const fileKey = key || basename(filePath)
  const fileStream = createReadStream(filePath)

  const upload = new Upload({
    client: s3Client,
    params: {
      Bucket: bucket,
      Key: fileKey,
      Body: fileStream,
      ContentType: contentType || getContentType(filePath),
      ...(acl && { ACL: acl }),
    },
    // 100MB part size for large files
    partSize: 100 * 1024 * 1024,
    // Upload 4 parts concurrently
    queueSize: 4,
  })

  await upload.done()

  return {
    bucket,
    key: fileKey,
    location: `https://${bucket}.s3.${credentials.region}.amazonaws.com/${fileKey}`,
  }
}

function getContentType(filePath: string): string {
  const ext = filePath.toLowerCase().split('.').pop()
  const mimeTypes: Record<string, string> = {
    json: 'application/json',
    ndjson: 'application/x-ndjson',
    csv: 'text/csv',
    txt: 'text/plain',
    html: 'text/html',
    xml: 'application/xml',
    pdf: 'application/pdf',
    png: 'image/png',
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    gif: 'image/gif',
    zip: 'application/zip',
    gz: 'application/gzip',
    xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    xls: 'application/vnd.ms-excel',
  }
  return mimeTypes[ext || ''] || 'application/octet-stream'
}


export const aws_regions = [
  { name: 'US East (N. Virginia)', region: 'us-east-1' },
  { name: 'US East (Ohio)', region: 'us-east-2' },
  { name: 'US West (N. California)', region: 'us-west-1' },
  { name: 'US West (Oregon)', region: 'us-west-2' },
  { name: 'Africa (Cape Town)', region: 'af-south-1' },
  { name: 'Asia Pacific (Hong Kong)', region: 'ap-east-1' },
  { name: 'Asia Pacific (Taipei)', region: 'ap-east-2' },
  { name: 'Asia Pacific (Mumbai)', region: 'ap-south-1' },
  { name: 'Asia Pacific (Hyderabad)', region: 'ap-south-2' },
  { name: 'Asia Pacific (Singapore)', region: 'ap-southeast-1' },
  { name: 'Asia Pacific (Sydney)', region: 'ap-southeast-2' },
  { name: 'Asia Pacific (Jakarta)', region: 'ap-southeast-3' },
  { name: 'Asia Pacific (Melbourne)', region: 'ap-southeast-4' },
  { name: 'Asia Pacific (Malaysia)', region: 'ap-southeast-5' },
  { name: 'Asia Pacific (New Zealand)', region: 'ap-southeast-6' },
  { name: 'Asia Pacific (Thailand)', region: 'ap-southeast-7' },
  { name: 'Asia Pacific (Tokyo)', region: 'ap-northeast-1' },
  { name: 'Asia Pacific (Seoul)', region: 'ap-northeast-2' },
  { name: 'Asia Pacific (Osaka)', region: 'ap-northeast-3' },
  { name: 'Canada (Central)', region: 'ca-central-1' },
  { name: 'Canada West (Calgary)', region: 'ca-west-1' },
  { name: 'Europe (Frankfurt)', region: 'eu-central-1' },
  { name: 'Europe (Zurich)', region: 'eu-central-2' },
  { name: 'Europe (Ireland)', region: 'eu-west-1' },
  { name: 'Europe (London)', region: 'eu-west-2' },
  { name: 'Europe (Paris)', region: 'eu-west-3' },
  { name: 'Europe (Milan)', region: 'eu-south-1' },
  { name: 'Europe (Spain)', region: 'eu-south-2' },
  { name: 'Europe (Stockholm)', region: 'eu-north-1' },
  { name: 'Israel (Tel Aviv)', region: 'il-central-1' },
  { name: 'Middle East (Bahrain)', region: 'me-south-1' },
  { name: 'Middle East (UAE)', region: 'me-central-1' },
  { name: 'South America (Sao Paulo)', region: 'sa-east-1' },
]

