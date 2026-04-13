package main

import (
	"fmt"
	"log"
	"os"

	"backend-api/internal/handler"

	"github.com/gofiber/fiber/v2"
	"github.com/joho/godotenv"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"backend-api/internal/domain"
	"backend-api/internal/repository"
)

func main() {

	err := godotenv.Load()
	if err != nil {
		log.Println("ไม่มีไฟล์ .env จะใช้ Environment Variables ของระบบแทน")
	}

	// .env
	dbHost := os.Getenv("DB_HOST")
	dbUser := os.Getenv("DB_USER")
	dbPassword := os.Getenv("DB_PASSWORD")
	dbName := os.Getenv("DB_NAME")
	dbPort := os.Getenv("DB_PORT")

	if dbHost == "" || dbUser == "" || dbPort == "" {
		log.Fatal("Eror: โหลด Environment Variables ไม่ครบ!")
	}

	// Connection String
	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=disable TimeZone=Asia/Bangkok",
		dbHost, dbUser, dbPassword, dbName, dbPort)

	// GORM Postgres
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatal("เชื่อมต่อ Database ไม่สำเร็จ:", err)
	}
	fmt.Println("เชื่อมต่อ Database สำเร็จแล้ว!")

	// Auto Migrate
	db.AutoMigrate(&domain.MangaMaster{})
	db.AutoMigrate(&domain.PhoenixManga{})
	db.AutoMigrate(&domain.MangaMLFeature{})
	fmt.Println("อัปเดตโครงสร้างตารางเรียบร้อย")

	mangaRepo := repository.NewMangaRepository(db)
	mangaHandler := handler.NewMangaHandler(mangaRepo)


	app := fiber.New()
	app.Post("/api/manga", mangaHandler.HandleUpsert)
	app.Get("/api/manga/pending", mangaHandler.HandleGetPending)
	app.Post("/api/manga/impute-titles", mangaHandler.ImputeTitles)
	app.Post("api/manga/generate-features", mangaHandler.GenerateFeatures)


	app.Get("/", func(c *fiber.Ctx) error {
		return c.SendString("Go API Server is running!")
	})

	fmt.Println("กำลังเปิด Server ที่พอร์ต :8080")
	log.Fatal(app.Listen(":8080"))

}