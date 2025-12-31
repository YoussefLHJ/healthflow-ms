// middleware.ts (in root directory)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // const token = request.cookies.get('healthflow_token')?.value

  // // Protected routes
  // const protectedPaths = ['/dashboard', '/patients', '/pipeline', '/settings']
  // const isProtectedPath = protectedPaths.some(path => 
  //   request.nextUrl.pathname.startsWith(path)
  // )

  // // If accessing protected route without token, redirect to login
  // if (isProtectedPath && !token) {
  //   const loginUrl = new URL('/login', request.url)
  //   loginUrl.searchParams.set('redirect', request.nextUrl.pathname)
  //   return NextResponse.redirect(loginUrl)
  // }

  // // If accessing login page with valid token, redirect to dashboard
  // if (request.nextUrl.pathname === '/login' && token) {
  //   return NextResponse.redirect(new URL('/dashboard', request.url))
  // }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/patients/:path*',
    '/pipeline/:path*',
    '/settings/:path*',
    '/login',
  ],
}
