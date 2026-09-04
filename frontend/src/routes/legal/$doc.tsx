import { createFileRoute } from "@tanstack/react-router";
import { LegalDocumentPage } from "@pages/legal";

/* Один динамический маршрут на все шесть документов: адреса задаёт реестр на бэкенде
   (`app/core/legal.py`), и заводить по файлу на каждый значило бы держать вторую копию
   этого реестра во фронте. Седьмой документ откроется сам. */
export const Route = createFileRoute("/legal/$doc")({
  component: LegalDocumentPage,
});
