
import dotenv from "dotenv";
dotenv.config();


import { getOrcaClient } from "@_koii/task-manager/extensions";
export async function handleOrcaClientCreation(){
    try {
      // if (process.env.NODE_ENV !== "development") {
        // const { getOrcaClient } = await import("@_koii/task-manager/extensions");
        const orcaClient = await getOrcaClient();
        if (!orcaClient) {
            throw new Error("Orca client not found");
        }
        return orcaClient;
      // }else{
      //   return null;
      // }
    }catch{
        throw new Error("Orca client not found");
    }
}
export async function handleRequest({orcaClient, route, bodyJSON}:{orcaClient:any, route:string, bodyJSON:any}){
    // if (process.env.NODE_ENV === "development") {
    //     const response = await fetch(`${process.env.LOCAL_CONTAINER_TEST_URL}/${route}`, {
    //       method: "POST",
    //       headers: {
    //         "Content-Type": "application/json",
    //       },
    //       body: JSON.stringify(bodyJSON),
    //     });
    //     return response;
    //   }else{
        if (!orcaClient) {
            throw new Error("Orca client not found");
        }
        const response = await orcaClient.podCall(`${route}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
            body: JSON.stringify(bodyJSON),
          });
        return response;
      // }
}
