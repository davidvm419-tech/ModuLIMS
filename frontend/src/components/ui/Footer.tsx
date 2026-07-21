export default function Footer() {
    return (
        <footer className="mt-auto pt-12 text-center text-xs text-gray-500">
            <div className="border-t border-interactive/10 pt-6">
                <p>© {new Date().getFullYear()} Microbial Systems. Todos los derechos reservados.</p>
                <p className="mt-1 text-gray-400">ModuLims - Laboratory Information Management System v1.0</p>
            </div>
        </footer>
    )
}