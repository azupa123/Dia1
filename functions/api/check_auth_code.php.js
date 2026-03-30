const AVATAR_FILE = "69ad879cb2271_6861408193_1772980124.jpg";
const SIGNATURE_FILE = "69ad87c37f602_6861408193_1772980163.png";

function json(payload) {
  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "Access-Control-Allow-Origin": "*",
    },
  });
}

export async function onRequestPost() {
  const avatarUrl = `/api/avatars/${AVATAR_FILE}`;
  const signatureUrl = `/api/signature/${SIGNATURE_FILE}`;

  return json({
    ok: true,
    authorized: true,
    uuid: "cf-pages-uuid",
    cord: "50.4501,30.5234",
    name: "Ісматов Андрій Валерович",
    fullName: "Ісматов Андрій Валерович",
    avatarUrl,
    signatureUrl,
    documents: [
      {
        type: "documents-passport",
        sortable: true,
        name: "Ісматов Андрій Валерович",
        birthday: "1990-01-01",
        photo: avatarUrl,
        sign: signatureUrl,
        number: "AA000000",
        color: "#e6f2ff",
      },
    ],
  });
}

export async function onRequestGet() {
  return onRequestPost();
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}
