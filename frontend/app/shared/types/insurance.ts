import { z } from "zod";

// Insurance schema
export const insuranceSchema = z.object({
  id: z.number(),
  number: z.string(),
  title: z.string(),
  description: z.string().nullable(),
});

export type Insurance = z.infer<typeof insuranceSchema>;

// Paginated insurance response
export const paginatedInsuranceSchema = z.object({
  items: z.array(insuranceSchema),
  total: z.number(),
  page: z.number(),
  page_size: z.number(),
  total_pages: z.number(),
});

export type PaginatedInsurance = z.infer<typeof paginatedInsuranceSchema>;
