const axios = require("axios");
require("dotenv").config();

const JUDGE0_URL = process.env.JUDGE0_URL || "http://localhost:2358";
const JUDGE0_API_KEY = process.env.JUDGE0_API_KEY || "";

const LANGUAGE_IDS = {
  python: 71,
  javascript: 63,
  typescript: 74,
  java: 62,
  cpp: 54,
  csharp: 51,
  go: 60,
  rust: 73,
  php: 68,
  swift: 83,
  kotlin: 78,
};

async function submitCode({ sourceCode, language, stdin, expectedOutput, cpuTimeLimit = 2, memoryLimit = 262144 }) {
  const languageId = LANGUAGE_IDS[language] || 71;

  const { data } = await axios.post(
    `${JUDGE0_URL}/submissions`,
    {
      source_code: sourceCode,
      language_id: languageId,
      stdin: stdin || "",
      expected_output: expectedOutput || "",
      cpu_time_limit: cpuTimeLimit,
      memory_limit: memoryLimit,
    },
    {
      headers: {
        "Content-Type": "application/json",
        "X-Auth-Token": JUDGE0_API_KEY,
      },
      params: { base64_encoded: "false", wait: "true", fields: "*" },
    }
  );

  return {
    token: data.token,
    statusId: data.status?.id,
    statusDescription: data.status?.description,
    stdout: data.stdout,
    stderr: data.stderr,
    compileOutput: data.compile_output,
    time: data.time,
    memory: data.memory,
  };
}

module.exports = { submitCode, LANGUAGE_IDS };
