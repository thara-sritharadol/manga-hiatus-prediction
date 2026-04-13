package handler

import (
	"backend-api/internal/domain"
	"backend-api/internal/repository"

	"github.com/gofiber/fiber/v2"
)

type MangaHandler struct {
	Repo *repository.MangaRepository
}

func NewMangaHandler(repo *repository.MangaRepository) *MangaHandler {
	return &MangaHandler{Repo: repo}
}

func (h *MangaHandler) HandleUpsert(c *fiber.Ctx) error {
	manga := new(domain.PhoenixManga)

	// แกะ JSON
	if err := c.BodyParser(manga); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": err.Error()})
	}

	// เรียกใช้ Repository
	if err := h.Repo.Upsert(manga); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "DB Error", "details": err.Error()})
	}

	return c.Status(fiber.StatusCreated).JSON(fiber.Map{
		"message": "Save Successfully!",
		"data":    manga,
	})
}

func (h *MangaHandler) HandleGetPending(c *fiber.Ctx) error {
	statusQuery := c.Query("status", "PENDING")
	// เรียกใช้ Repo
	mangas, err := h.Repo.GetPendingByStatus(statusQuery)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "ไม่สามารถดึงข้อมูลจาก Database ได้",
			"details": err.Error(),
		})
	}

	// ตอบกลับเป็น JSON พร้อมบอกจำนวน (Count) ให้ฝั่ง Python รู้
	return c.Status(fiber.StatusOK).JSON(fiber.Map{
		"message": "ดึงข้อมูลสำเร็จ",
		"count":   len(mangas),
		"data":    mangas,
	})
}

func (h *MangaHandler) ImputeTitles(c *fiber.Ctx) error {
	// เรียกใช้ฟังก์ชันจาก Repository (เหมือนเดิม)
	rowsAffected, err := h.Repo.ImputeEnglishTitles()
	
	if err != nil {
		// ส่ง HTTP 500 กลับไปพร้อมรายละเอียด
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error":   "Failed to impute titles",
			"details": err.Error(),
		})
	}

	// ส่ง HTTP 200 (OK) กลับไปเมื่อทำงานสำเร็จ
	return c.Status(fiber.StatusOK).JSON(fiber.Map{
		"message":      "Title imputation successful",
		"updated_rows": rowsAffected,
	})
}

func (h *MangaHandler) GenerateFeatures(c *fiber.Ctx) error {
	// Call repository to generate ML features
	if err := h.Repo.GenerateMLFeatures(); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error":   "Failed to generate ML features",
			"details": err.Error(),
		})
	}

	// Return success response
	return c.Status(fiber.StatusOK).JSON(fiber.Map{
		"message": "ML features generated successfully",
	})
}