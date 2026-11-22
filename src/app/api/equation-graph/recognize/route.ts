import { NextRequest, NextResponse } from "next/server";


const MAX_IMAGE_SIZE = 8 * 1024 * 1024;

export async function POST(request: NextRequest) {
  try {
    const body: unknown = await request.json();

    if (
      typeof body !== "object" ||
      body === null ||
      !("image" in body) ||
      typeof body.image !== "string"
    ) {
      return NextResponse.json(
        { error: "A valid image is required." },
        { status: 400 },
      );
    }

    const image = body.image;
    const match = image.match(
      /^data:image\/(png|jpeg|webp);base64,([A-Za-z0-9+/]+={0,2})$/,
    );

    if (!match) {
      return NextResponse.json(
        { error: "Only PNG, JPEG and WebP images are supported." },
        { status: 415 },
      );
    }

    const mimeType = `image/${match[1]}`;
    const imageBuffer = Buffer.from(match[2], "base64");

    if (
      imageBuffer.length === 0 ||
      imageBuffer.length > MAX_IMAGE_SIZE
    ) {
      return NextResponse.json(
        { error: "Image is empty or exceeds the 8 MB limit." },
        { status: 413 },
      );
    }

    const apiUrl = process.env.EQUATION_OCR_API_URL;

    if (!apiUrl) {
      return NextResponse.json(
        { error: "OCR service URL is not configured." },
        { status: 500 },
      );
    }

    const formData = new FormData();

    formData.append(
      "file",
      new Blob([new Uint8Array(imageBuffer)], {
        type: mimeType,
      }),
      `equation.${match[1]}`,
    );

    const upstream = await fetch(
      `${apiUrl.replace(/\/+$/, "")}/recognize`,
      {
        method: "POST",
        body: formData,
        cache: "no-store",
        signal: AbortSignal.timeout(60_000),
      },
    );

    const result: unknown = await upstream.json();

    if (!upstream.ok) {
      return NextResponse.json(
        { error: "OCR service could not recognize the image." },
        { status: upstream.status },
      );
    }

    if (
      typeof result !== "object" ||
      result === null ||
      !("latex" in result) ||
      typeof result.latex !== "string" ||
      !("score" in result) ||
      typeof result.score !== "number"
    ) {
      return NextResponse.json(
        { error: "OCR service returned an invalid response." },
        { status: 502 },
      );
    }

    return NextResponse.json({
      success: true,
      latex: result.latex,
      score: result.score,
    });
  } catch (error) {
    console.error("Equation OCR proxy error:", error);

    return NextResponse.json(
      { error: "Unable to connect to the OCR service." },
      { status: 502 },
    );
  }
}
