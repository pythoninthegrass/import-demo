import "dotenv/config";
import fs from "fs";
import axios from "axios";
import { gql, GraphQLClient } from "graphql-request";

const API_URL =
  process.env.API_URL ?? "https://api-prod.omnivore.app/api/graphql";

// https://github.com/omnivore-app/omnivore/blob/main/packages/api/src/schema.ts
const uploadImportFileMutation = gql`
  mutation UploadImportFile(
    $type: UploadImportFileType!
    $contentType: String!
  ) {
    uploadImportFile(type: $type, contentType: $contentType) {
      ... on UploadImportFileError {
        errorCodes
      }
      ... on UploadImportFileSuccess {
        uploadSignedUrl
      }
    }
  }
`;

async function main() {
  console.log("Connecting to ", API_URL);
  if (!process.env.API_KEY) {
    throw new Error(
      "No auth token found. Did you forget to add it to the .env file?"
    );
  }

  const client = new GraphQLClient(API_URL, {
    headers: {
      Authorization: process.env.API_KEY,
    },
  });

  const importFile = fs.readFileSync("import.csv");

  const response = await client.request(uploadImportFileMutation, {
    type: "URL_LIST",
    contentType: "text/csv",
  });

  if (response && response.uploadImportFile.uploadSignedUrl) {
    try {
      const uploadRes = await axios.put(
        response.uploadImportFile.uploadSignedUrl,
        importFile,
        {
          method: "PUT",
          headers: {
            "content-type": "text/csv",
            "content-length": importFile.byteLength,
          },
        }
      );
    } catch (err) {
      console.log("error uploading:", err);
    }
  } else {
    console.log("error response: " + response);
  }

  console.log(`Successfully started import.`);
}

main();
