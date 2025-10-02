const { ChatOpenAI } = require("@langchain/openai");
const { PromptTemplate } = require("@langchain/core/prompts");
const { StructuredOutputParser } = require("langchain/output_parsers");
const { z } = require("zod");
const path = require("path");

// Load .env from project root (two levels up from services/web/)
require("dotenv").config({ path: path.join(__dirname, "../../.env") });

const playerInfoSchema = z.object({
  name: z.string().describe("The player's name"),
  image_url: z.string().describe("The player's image URL"),
  national_team: z.string().describe("The player's country"),
  dob: z
    .string()
    .describe(
      "The player's birth date as a string (e.g., '1992-04-18' or 'April 18, 1992')"
    ),
  birth_place: z.string().describe("The player's birth place"),
  gender: z.string().describe("The player's gender"),
  batting_styles: z
    .array(z.string())
    .describe("The player's batting style (e.g., Right-hand bat)"),
  bowling_styles: z
    .array(z.string())
    .optional()
    .describe("The player's bowling style (e.g., Right-arm medium)"),
  fielding_position: z
    .string()
    .optional()
    .describe("The player's fielding position (e.g., Wicket-keeper)"),
  playing_role: z
    .string()
    .describe("The player's role in the team (e.g., Wicket-keeper batsman)"),
  is_active: z
    .boolean()
    .describe("Whether the player is active in cricket (e.g., true or false)"),
});

function createModel() {
  if (!process.env.OPENAI_API_KEY) {
    throw new Error("OPENAI_API_KEY environment variable is not set");
  }

  return new ChatOpenAI({
    modelName: process.env.OPENAI_MODEL,
    openAIApiKey: process.env.OPENAI_API_KEY,
  });
}

const parser = StructuredOutputParser.fromZodSchema(playerInfoSchema);

function parseAIResponse(text) {
  try {
    let cleanText = text.trim();
    if (cleanText.startsWith("```json")) {
      cleanText = cleanText.replace(/^```json\s*/, "").replace(/\s*```$/, "");
    } else if (cleanText.startsWith("```")) {
      cleanText = cleanText.replace(/^```\s*/, "").replace(/\s*```$/, "");
    }

    return JSON.parse(cleanText);
  } catch (error) {
    throw new Error(`JSON parsing failed: ${error.message}`);
  }
}

async function scrapePlayerInfoWithAI(playerId) {
  try {
    const url = `https://www.espncricinfo.com/ci/content/player/${playerId}.html`;

    const html = await fetch(url).then((res) => res.text());

    const model = createModel();

    const prompt = PromptTemplate.fromTemplate(`
        You are a cricket information expert with comprehensive knowledge of international and domestic cricket players.
        You are given a HTML page of a cricket player.
        Your task is to extract the player information from the HTML page. 
        
        {html}

        Instructions:
        - Provide accurate real-world information based on the HTML page
        - Ensure all information is factual and up-to-date
        - Include personal details, cricket-specific information, and career background

        Required information to provide:
        - Personal details (full name, birth info, physical attributes)
        - Cricket-specific information (batting/bowling style, role)

        {format_instructions}

        IMPORTANT: Return ONLY valid JSON data. Do not wrap the response in markdown code blocks or include any explanatory text. The response should be pure JSON that can be directly parsed.
        `);

    const formatInstructions = parser.getFormatInstructions();

    const chain = prompt.pipe(model);

    const aiResponse = await chain.invoke({
      html: html,
      format_instructions: formatInstructions,
    });

    const parsedData = parseAIResponse(aiResponse.content);

    const result = playerInfoSchema.parse(parsedData);

    return {
      player_info: result,
      scraped_at: new Date().toISOString(),
    };
  } catch (error) {
    throw error;
  }
}

module.exports = {
  scrapePlayerInfoWithAI,
};
